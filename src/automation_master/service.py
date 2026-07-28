"""Application service for registry and event-sourced credit governance."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .models import (
    AutomationSpec,
    EnforcementMode,
    ReservationDecision,
    RunClass,
    new_event_id,
)
from .store import Event, EventStore


@dataclass(frozen=True)
class CreditPolicy:
    mode: EnforcementMode = EnforcementMode.DISABLED
    overdraft_limit: int = 0
    allow_critical_overdraft: bool = False
    exempt_run_classes: tuple[RunClass, ...] = (
        RunClass.UNIQUE,
        RunClass.SAFETY,
        RunClass.DEADLINE,
    )

    def validate(self) -> None:
        if self.overdraft_limit < 0:
            raise ValueError("overdraft_limit must be non-negative")


@dataclass(frozen=True)
class BudgetState:
    budget_epoch: str
    scope_id: str
    allocated: int
    transferred_in: int
    transferred_out: int
    held: int
    spent: int

    @property
    def envelope(self) -> int:
        return self.allocated + self.transferred_in - self.transferred_out

    @property
    def available(self) -> int:
        return self.envelope - self.held - self.spent

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["envelope"] = self.envelope
        result["available"] = self.available
        return result


@dataclass(frozen=True)
class ReceiptMetrics:
    budget_epoch: str
    scope_id: str
    total: int
    useful: int
    no_work: int
    errors: int

    @property
    def useful_rate(self) -> float:
        return self.useful / self.total if self.total else 0.0

    @property
    def no_work_rate(self) -> float:
        return self.no_work / self.total if self.total else 0.0

    @property
    def error_rate(self) -> float:
        return self.errors / self.total if self.total else 0.0

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result.update(
            {
                "useful_rate": self.useful_rate,
                "no_work_rate": self.no_work_rate,
                "error_rate": self.error_rate,
            }
        )
        return result


class AutomationMaster:
    """Facade whose durable state consists exclusively of immutable events."""

    def __init__(self, store: EventStore, *, node_id: str) -> None:
        if not node_id.strip():
            raise ValueError("node_id is required")
        self.store = store
        self.node_id = node_id

    def register_family(
        self,
        family_id: str,
        *,
        name: str,
        version: int = 1,
        budget_epoch: str = "registry",
        tombstone: bool = False,
    ) -> Event:
        return self.store.append(
            node_id=self.node_id,
            budget_epoch=budget_epoch,
            event_type="FAMILY_REGISTERED",
            entity_type="family",
            entity_id=family_id,
            event_version=version,
            tombstone=tombstone,
            dedupe_key=f"family:{family_id}:v{version}",
            payload={"family_id": family_id, "name": name, "version": version},
        )

    def register_automation(
        self,
        spec: AutomationSpec,
        *,
        budget_epoch: str = "registry",
        tombstone: bool = False,
    ) -> Event:
        return self.store.append(
            node_id=self.node_id,
            budget_epoch=budget_epoch,
            event_type="AUTOMATION_REGISTERED",
            entity_type="automation",
            entity_id=spec.automation_id,
            event_version=spec.version,
            tombstone=tombstone,
            dedupe_key=f"automation:{spec.automation_id}:v{spec.version}",
            payload=spec.as_payload(),
        )

    def registry(self) -> dict[str, dict[str, dict[str, Any]]]:
        latest: dict[tuple[str, str], Event] = {}
        for event in self.store.events(
            event_types=["FAMILY_REGISTERED", "AUTOMATION_REGISTERED"]
        ):
            key = (event.entity_type, event.entity_id)
            previous = latest.get(key)
            if previous is None or (event.event_version, event.event_id) > (
                previous.event_version,
                previous.event_id,
            ):
                latest[key] = event
        result: dict[str, dict[str, dict[str, Any]]] = {
            "families": {},
            "automations": {},
        }
        for (entity_type, entity_id), event in latest.items():
            if event.tombstone:
                continue
            bucket = "families" if entity_type == "family" else "automations"
            result[bucket][entity_id] = event.payload
        return result

    def allocate_budget(
        self,
        *,
        budget_epoch: str,
        scope_id: str,
        credits: int,
        allocation_id: str,
    ) -> Event:
        if credits < 0:
            raise ValueError("credits must be non-negative")
        return self.store.append(
            node_id=self.node_id,
            budget_epoch=budget_epoch,
            event_type="BUDGET_ALLOCATED",
            entity_type="budget-scope",
            entity_id=scope_id,
            dedupe_key=f"allocation:{budget_epoch}:{allocation_id}",
            payload={
                "allocation_id": allocation_id,
                "scope_id": scope_id,
                "credits": credits,
            },
        )

    def preflight(
        self,
        *,
        run_id: str,
        budget_epoch: str,
        scope_id: str,
        work_item_id: str,
        work_available: bool,
    ) -> ReservationDecision | None:
        payload = {
            "run_id": run_id,
            "scope_id": scope_id,
            "work_item_id": work_item_id,
            "work_available": work_available,
        }
        with self.store.immediate() as conn:
            self.store.append(
                node_id=self.node_id,
                budget_epoch=budget_epoch,
                event_type="ELIGIBILITY_CHECKED",
                entity_type="run",
                entity_id=run_id,
                dedupe_key=f"eligibility:{run_id}",
                payload=payload,
                connection=conn,
            )
            if work_available:
                return None
            existing = self.store.get(dedupe_key=f"credit-decision:{run_id}", connection=conn)
            if existing:
                return self._decision_from_event(existing)
            return self._append_decision(
                conn,
                budget_epoch=budget_epoch,
                run_id=run_id,
                scope_id=scope_id,
                status="NO_WORK",
                reservation_id=None,
                credits=0,
                available_before=self._budget_state(
                    budget_epoch, scope_id, connection=conn
                ).available,
                explanation="Preflight found no eligible work; no credit was consumed.",
                event_type="NO_WORK",
            )

    def reserve_credit(
        self,
        *,
        run_id: str,
        budget_epoch: str,
        scope_id: str,
        credits: int,
        run_class: RunClass,
        policy: CreditPolicy,
        critical_minimum_coverage: bool = False,
    ) -> ReservationDecision:
        if credits <= 0:
            raise ValueError("credits must be positive")
        policy.validate()
        with self.store.immediate() as conn:
            existing = self.store.get(dedupe_key=f"credit-decision:{run_id}", connection=conn)
            if existing:
                return self._decision_from_event(existing)
            eligibility = self.store.get(dedupe_key=f"eligibility:{run_id}", connection=conn)
            if eligibility is None:
                raise RuntimeError("preflight is required before credit reservation")
            if not eligibility.payload["work_available"]:
                return self._append_decision(
                    conn,
                    budget_epoch=budget_epoch,
                    run_id=run_id,
                    scope_id=scope_id,
                    status="NO_WORK",
                    reservation_id=None,
                    credits=0,
                    available_before=self._budget_state(
                        budget_epoch, scope_id, connection=conn
                    ).available,
                    explanation="Preflight found no eligible work.",
                    event_type="NO_WORK",
                )

            state = self._budget_state(budget_epoch, scope_id, connection=conn)
            available = state.available
            reservation_id = new_event_id()
            if policy.mode == EnforcementMode.DISABLED:
                return self._append_decision(
                    conn,
                    budget_epoch=budget_epoch,
                    run_id=run_id,
                    scope_id=scope_id,
                    status="ALLOWED_DISABLED",
                    reservation_id=None,
                    credits=0,
                    available_before=available,
                    explanation="Credit enforcement is disabled.",
                    event_type="CREDIT_EXEMPTED",
                )

            enough = available >= credits
            exempt = run_class in policy.exempt_run_classes
            deficit = max(0, credits - available)
            may_overdraw = (
                critical_minimum_coverage
                and policy.allow_critical_overdraft
                and deficit <= policy.overdraft_limit
            )
            if policy.mode == EnforcementMode.ENFORCED and not enough:
                if exempt:
                    return self._append_decision(
                        conn,
                        budget_epoch=budget_epoch,
                        run_id=run_id,
                        scope_id=scope_id,
                        status="EXEMPT_CRITICAL_CLASS",
                        reservation_id=None,
                        credits=0,
                        available_before=available,
                        explanation=f"{run_class.value} runs keep minimum coverage.",
                        event_type="CREDIT_EXEMPTED",
                    )
                if not may_overdraw:
                    return self._append_decision(
                        conn,
                        budget_epoch=budget_epoch,
                        run_id=run_id,
                        scope_id=scope_id,
                        status="BUDGET_DENIED",
                        reservation_id=None,
                        credits=credits,
                        available_before=available,
                        explanation="Comparable run has insufficient budget.",
                        event_type="BUDGET_DENIED",
                    )

            status = "RESERVED"
            if not enough:
                status = (
                    "SHADOW_NEGATIVE"
                    if policy.mode == EnforcementMode.SHADOW
                    else "BUDGET_OVERDRAFT"
                )
            decision = self._append_decision(
                conn,
                budget_epoch=budget_epoch,
                run_id=run_id,
                scope_id=scope_id,
                status=status,
                reservation_id=reservation_id,
                credits=credits,
                available_before=available,
                explanation=(
                    "Reservation recorded."
                    if enough
                    else "Reservation recorded with a bounded negative envelope."
                ),
                event_type="CREDIT_RESERVED",
            )
            if not enough:
                self.store.append(
                    node_id=self.node_id,
                    budget_epoch=budget_epoch,
                    event_type="OVERDRAFT_RECORDED",
                    entity_type="reservation",
                    entity_id=reservation_id,
                    dedupe_key=f"overdraft:{reservation_id}",
                    payload={
                        "run_id": run_id,
                        "scope_id": scope_id,
                        "reservation_id": reservation_id,
                        "deficit": deficit,
                        "mode": policy.mode.value,
                    },
                    connection=conn,
                )
            return decision

    def complete_run(
        self,
        *,
        run_id: str,
        outcome: str,
        useful: bool,
        details: dict[str, Any] | None = None,
    ) -> Event:
        with self.store.immediate() as conn:
            existing = self.store.get(dedupe_key=f"receipt:{run_id}", connection=conn)
            if existing:
                expected = {
                    "run_id": run_id,
                    "outcome": outcome,
                    "useful": useful,
                    "details": details or {},
                }
                if existing.payload != expected:
                    raise ValueError("run already has a different receipt")
                return existing
            decision_event = self.store.get(
                dedupe_key=f"credit-decision:{run_id}", connection=conn
            )
            if decision_event is None:
                raise RuntimeError("credit decision is required before completion")
            receipt = self.store.append(
                node_id=self.node_id,
                budget_epoch=decision_event.budget_epoch,
                event_type="RECEIPT_RECORDED",
                entity_type="run",
                entity_id=run_id,
                dedupe_key=f"receipt:{run_id}",
                payload={
                    "run_id": run_id,
                    "outcome": outcome,
                    "useful": useful,
                    "details": details or {},
                },
                connection=conn,
            )
            reservation_id = decision_event.payload.get("reservation_id")
            if reservation_id:
                transition = "CREDIT_RELEASED" if outcome == "NO_WORK" else "CREDIT_CONSUMED"
                self.store.append(
                    node_id=self.node_id,
                    budget_epoch=decision_event.budget_epoch,
                    event_type=transition,
                    entity_type="reservation",
                    entity_id=reservation_id,
                    dedupe_key=f"reservation-result:{reservation_id}",
                    payload={
                        "run_id": run_id,
                        "scope_id": decision_event.payload["scope_id"],
                        "reservation_id": reservation_id,
                        "credits": decision_event.payload["credits"],
                        "outcome": outcome,
                    },
                    connection=conn,
                )
            return receipt

    def handover_budget(
        self,
        *,
        budget_epoch: str,
        source_scope_id: str,
        target_scope_id: str,
        credits: int,
        transfer_id: str,
    ) -> tuple[Event, Event]:
        if credits <= 0:
            raise ValueError("credits must be positive")
        with self.store.immediate() as conn:
            source = self._budget_state(budget_epoch, source_scope_id, connection=conn)
            if source.available < credits:
                raise RuntimeError("insufficient transferable budget")
            common = {
                "transfer_id": transfer_id,
                "source_scope_id": source_scope_id,
                "target_scope_id": target_scope_id,
                "credits": credits,
            }
            outgoing = self.store.append(
                node_id=self.node_id,
                budget_epoch=budget_epoch,
                event_type="BUDGET_HANDOVER_OUT",
                entity_type="budget-scope",
                entity_id=source_scope_id,
                dedupe_key=f"handover:{budget_epoch}:{transfer_id}:out",
                payload=common,
                connection=conn,
            )
            incoming = self.store.append(
                node_id=self.node_id,
                budget_epoch=budget_epoch,
                event_type="BUDGET_HANDOVER_IN",
                entity_type="budget-scope",
                entity_id=target_scope_id,
                dedupe_key=f"handover:{budget_epoch}:{transfer_id}:in",
                payload=common,
                connection=conn,
            )
            return outgoing, incoming

    def return_budget(
        self,
        *,
        budget_epoch: str,
        source_scope_id: str,
        target_scope_id: str,
        credits: int,
        transfer_id: str,
    ) -> tuple[Event, Event]:
        return self.handover_budget(
            budget_epoch=budget_epoch,
            source_scope_id=source_scope_id,
            target_scope_id=target_scope_id,
            credits=credits,
            transfer_id=f"return:{transfer_id}",
        )

    def record_human_override(
        self,
        *,
        budget_epoch: str,
        override_id: str,
        target_type: str,
        target_id: str,
        value: dict[str, Any],
        actor: str,
        reason: str,
        version: int,
    ) -> Event:
        if not actor.strip() or not reason.strip():
            raise ValueError("actor and reason are required")
        return self.store.append(
            node_id=self.node_id,
            budget_epoch=budget_epoch,
            event_type="HUMAN_OVERRIDE",
            entity_type=target_type,
            entity_id=target_id,
            event_version=version,
            dedupe_key=f"human-override:{override_id}:v{version}",
            payload={
                "override_id": override_id,
                "target_type": target_type,
                "target_id": target_id,
                "value": value,
                "actor": actor,
                "reason": reason,
                "version": version,
            },
        )

    def receipt_metrics(self, budget_epoch: str, scope_id: str) -> ReceiptMetrics:
        events = self.store.events(budget_epoch=budget_epoch)
        run_scopes = {
            event.entity_id: event.payload["scope_id"]
            for event in events
            if event.dedupe_key
            and event.dedupe_key.startswith("credit-decision:")
            and "scope_id" in event.payload
        }
        receipts = [
            event
            for event in events
            if event.event_type == "RECEIPT_RECORDED"
            and run_scopes.get(event.entity_id) == scope_id
        ]
        error_outcomes = {"ERROR", "FAILED", "ABORTED"}
        return ReceiptMetrics(
            budget_epoch=budget_epoch,
            scope_id=scope_id,
            total=len(receipts),
            useful=sum(bool(event.payload["useful"]) for event in receipts),
            no_work=sum(event.payload["outcome"].upper() == "NO_WORK" for event in receipts),
            errors=sum(
                event.payload["outcome"].upper() in error_outcomes for event in receipts
            ),
        )

    def propose_throttle(
        self,
        *,
        budget_epoch: str,
        scope_id: str,
        policy_version: int,
    ) -> Event:
        metrics = self.receipt_metrics(budget_epoch, scope_id)
        if metrics.total < 3:
            action = "observe"
            reason = "insufficient sample"
        elif metrics.error_rate >= 0.25:
            action = "pause-review"
            reason = "error-rate threshold reached"
        elif metrics.no_work_rate >= 0.75:
            action = "reduce"
            reason = "no-work-rate threshold reached"
        elif metrics.useful_rate >= 0.75:
            action = "maintain-or-increase"
            reason = "high useful-result rate"
        else:
            action = "maintain"
            reason = "no threshold reached"
        return self.store.append(
            node_id=self.node_id,
            budget_epoch=budget_epoch,
            event_type="THROTTLE_PROPOSED",
            entity_type="budget-scope",
            entity_id=scope_id,
            event_version=policy_version,
            dedupe_key=f"throttle:{budget_epoch}:{scope_id}:v{policy_version}",
            payload={
                "scope_id": scope_id,
                "policy_version": policy_version,
                "action": action,
                "reason": reason,
                "metrics": metrics.as_dict(),
            },
        )

    def overdraft_alerts(self, budget_epoch: str) -> list[dict[str, Any]]:
        """Return bounded warning records for an optional `.SYNC` exporter."""

        return [
            {
                "event_id": event.event_id,
                "node_id": event.node_id,
                "budget_epoch": event.budget_epoch,
                "run_id": event.payload["run_id"],
                "scope_id": event.payload["scope_id"],
                "deficit": event.payload["deficit"],
                "mode": event.payload["mode"],
                "payload_hash": event.payload_hash,
            }
            for event in self.store.events(
                budget_epoch=budget_epoch,
                event_types=["OVERDRAFT_RECORDED"],
            )
        ]

    def budget_state(self, budget_epoch: str, scope_id: str) -> BudgetState:
        return self._budget_state(budget_epoch, scope_id)

    def _budget_state(
        self,
        budget_epoch: str,
        scope_id: str,
        *,
        connection: Any | None = None,
    ) -> BudgetState:
        events = self.store.events(budget_epoch=budget_epoch, connection=connection)
        allocated = transferred_in = transferred_out = spent = 0
        reservations: dict[str, int] = {}
        transitions: dict[str, Event] = {}
        for event in events:
            payload = event.payload
            if event.event_type == "BUDGET_ALLOCATED" and payload["scope_id"] == scope_id:
                allocated += int(payload["credits"])
            elif (
                event.event_type == "BUDGET_HANDOVER_IN"
                and payload["target_scope_id"] == scope_id
            ):
                transferred_in += int(payload["credits"])
            elif (
                event.event_type == "BUDGET_HANDOVER_OUT"
                and payload["source_scope_id"] == scope_id
            ):
                transferred_out += int(payload["credits"])
            elif event.event_type == "CREDIT_RESERVED" and payload["scope_id"] == scope_id:
                reservation = payload.get("reservation_id")
                if reservation:
                    reservations[reservation] = int(payload["credits"])
            elif event.event_type in {"CREDIT_RELEASED", "CREDIT_CONSUMED"}:
                if payload["scope_id"] != scope_id:
                    continue
                reservation = payload["reservation_id"]
                previous = transitions.get(reservation)
                if previous is None or event.event_id > previous.event_id:
                    transitions[reservation] = event
        for reservation, transition in transitions.items():
            if transition.event_type == "CREDIT_CONSUMED":
                spent += int(transition.payload["credits"])
            reservations.pop(reservation, None)
        return BudgetState(
            budget_epoch,
            scope_id,
            allocated,
            transferred_in,
            transferred_out,
            sum(reservations.values()),
            spent,
        )

    def _append_decision(
        self,
        conn: Any,
        *,
        budget_epoch: str,
        run_id: str,
        scope_id: str,
        status: str,
        reservation_id: str | None,
        credits: int,
        available_before: int,
        explanation: str,
        event_type: str,
    ) -> ReservationDecision:
        decision = ReservationDecision(
            status=status,
            run_id=run_id,
            reservation_id=reservation_id,
            credits=credits,
            available_before=available_before,
            explanation=explanation,
        )
        payload = decision.as_dict() | {"scope_id": scope_id}
        event = self.store.append(
            node_id=self.node_id,
            budget_epoch=budget_epoch,
            event_type=event_type,
            entity_type="run",
            entity_id=run_id,
            dedupe_key=f"credit-decision:{run_id}",
            payload=payload,
            connection=conn,
        )
        return self._decision_from_event(event)

    @staticmethod
    def _decision_from_event(event: Event) -> ReservationDecision:
        return ReservationDecision(
            status=event.payload["status"],
            run_id=event.payload["run_id"],
            reservation_id=event.payload.get("reservation_id"),
            credits=int(event.payload["credits"]),
            available_before=int(event.payload["available_before"]),
            explanation=event.payload["explanation"],
        )
