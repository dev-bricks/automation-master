"""Fail-closed deployment-plan validation for System-Gap-Master integrations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..models import EnforcementMode, content_hash


@dataclass(frozen=True)
class DeploymentPlan:
    module_id: str
    module_version: str
    source_id: str
    target_node: str
    target_path: str
    manifest_hash: str
    mode: EnforcementMode = EnforcementMode.DISABLED
    activate: bool = False

    def canonical_payload(self) -> dict[str, Any]:
        result = asdict(self)
        result["mode"] = self.mode.value
        return result


@dataclass(frozen=True)
class TrustPolicy:
    allowed_sources: tuple[str, ...] = ()
    allowed_target_roots: tuple[str, ...] = ()
    allowed_modes: tuple[EnforcementMode, ...] = (
        EnforcementMode.DISABLED,
        EnforcementMode.SHADOW,
    )
    allow_activation: bool = False


class SystemGapAdapter:
    def __init__(self, *, local_node: str, trust_policy: TrustPolicy | None = None) -> None:
        self.local_node = local_node
        self.trust_policy = trust_policy or TrustPolicy()

    @staticmethod
    def manifest_hash(manifest: dict[str, Any]) -> str:
        return content_hash(manifest)

    def validate(
        self,
        plan: DeploymentPlan,
        *,
        manifest: dict[str, Any],
        installed_version: str | None = None,
    ) -> list[str]:
        errors: list[str] = []
        if plan.module_id != "automation-master":
            errors.append("foreign module_id")
        if plan.target_node != self.local_node:
            errors.append("foreign target_node")
        if plan.source_id not in self.trust_policy.allowed_sources:
            errors.append("untrusted source_id")
        if plan.mode not in self.trust_policy.allowed_modes:
            errors.append("enforcement mode not allowed")
        if plan.activate and not self.trust_policy.allow_activation:
            errors.append("activation not allowed")
        if self.manifest_hash(manifest) != plan.manifest_hash:
            errors.append("manifest hash mismatch")
        manifest_id = str(manifest.get("id", ""))
        if manifest_id != plan.module_id:
            errors.append("manifest module_id mismatch")
        manifest_version = str(manifest.get("version", ""))
        if manifest_version != plan.module_version:
            errors.append("manifest version mismatch")
        try:
            plan_version = self._version_tuple(plan.module_version)
            manifest_version_tuple = self._version_tuple(manifest_version)
            if plan_version != manifest_version_tuple:
                errors.append("semantic version mismatch")
            if installed_version and self._version_tuple(installed_version) > plan_version:
                errors.append("downgrade blocked")
        except ValueError as exc:
            errors.append(str(exc))
        if not self._target_allowed(plan.target_path):
            errors.append("target path outside trusted roots")
        return errors

    def require_valid(
        self,
        plan: DeploymentPlan,
        *,
        manifest: dict[str, Any],
        installed_version: str | None = None,
    ) -> None:
        errors = self.validate(plan, manifest=manifest, installed_version=installed_version)
        if errors:
            raise ValueError("; ".join(errors))

    def healthcheck(self, plan: DeploymentPlan, *, observed_hash: str) -> bool:
        return plan.manifest_hash == observed_hash

    def rollback_plan(self, plan: DeploymentPlan, *, previous_version: str) -> dict[str, str]:
        return {
            "module_id": plan.module_id,
            "target_node": plan.target_node,
            "target_path": plan.target_path,
            "restore_version": previous_version,
            "activation": "disabled",
        }

    def _target_allowed(self, target_path: str) -> bool:
        target = Path(target_path).expanduser().resolve()
        for root_text in self.trust_policy.allowed_target_roots:
            root = Path(root_text).expanduser().resolve()
            if target == root or root in target.parents:
                return True
        return False

    @staticmethod
    def _version_tuple(version: str) -> tuple[int, int, int]:
        parts = version.split(".")
        if len(parts) != 3 or any(not part.isdigit() for part in parts):
            raise ValueError(f"invalid semantic version: {version}")
        return int(parts[0]), int(parts[1]), int(parts[2])
