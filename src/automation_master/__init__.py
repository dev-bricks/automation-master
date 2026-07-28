"""Public API for automation-master."""

from .models import (
    AutomationSpec,
    EnforcementMode,
    MutationClass,
    ReservationDecision,
    RewardSignals,
    RunClass,
)
from .reward import RewardPolicy, RewardResult
from .service import AutomationMaster, BudgetState, CreditPolicy, ReceiptMetrics
from .store import EventConflictError, EventStore

__all__ = [
    "AutomationMaster",
    "AutomationSpec",
    "BudgetState",
    "CreditPolicy",
    "EnforcementMode",
    "EventConflictError",
    "EventStore",
    "MutationClass",
    "ReservationDecision",
    "ReceiptMetrics",
    "RewardPolicy",
    "RewardResult",
    "RewardSignals",
    "RunClass",
]

__version__ = "0.1.0"
