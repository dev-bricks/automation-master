"""Integration adapters. Core governance never starts or schedules processes."""

from .scheduler import CreditGateAdapter
from .sqlite_transit import AutomationEventMergePolicy
from .system_gap import DeploymentPlan, SystemGapAdapter, TrustPolicy

__all__ = [
    "AutomationEventMergePolicy",
    "CreditGateAdapter",
    "DeploymentPlan",
    "SystemGapAdapter",
    "TrustPolicy",
]
