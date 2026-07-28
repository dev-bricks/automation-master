"""Narrow scheduler credit-gate contract."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import ReservationDecision, RunClass
from ..service import AutomationMaster, CreditPolicy


@dataclass
class CreditGateAdapter:
    master: AutomationMaster
    policy: CreditPolicy

    def authorize(
        self,
        *,
        run_id: str,
        budget_epoch: str,
        scope_id: str,
        work_item_id: str,
        work_available: bool,
        credits: int,
        run_class: RunClass = RunClass.COMPARABLE,
        critical_minimum_coverage: bool = False,
    ) -> ReservationDecision:
        no_work = self.master.preflight(
            run_id=run_id,
            budget_epoch=budget_epoch,
            scope_id=scope_id,
            work_item_id=work_item_id,
            work_available=work_available,
        )
        if no_work:
            return no_work
        return self.master.reserve_credit(
            run_id=run_id,
            budget_epoch=budget_epoch,
            scope_id=scope_id,
            credits=credits,
            run_class=run_class,
            policy=self.policy,
            critical_minimum_coverage=critical_minimum_coverage,
        )
