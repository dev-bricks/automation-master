"""Public API for automation-master."""

from .adapters.prompt_repair import (
    AntigravityPromptRepairContractAdapter,
    PromptRepairContractAdapter,
    PromptRepairContractError,
    PromptRepairContractResult,
)
from .models import (
    AutomationSpec,
    EnforcementMode,
    MutationClass,
    ReservationDecision,
    RewardSignals,
    RunClass,
)
from .retention import (
    ReceiptRetentionClass,
    ReceiptRetentionPolicy,
    project_receipt,
    project_receipts,
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
    "ReceiptRetentionClass",
    "ReceiptRetentionPolicy",
    "RunClass",
    "AntigravityPromptRepairContractAdapter",
    "PromptRepairContractAdapter",
    "PromptRepairContractError",
    "PromptRepairContractResult",
    "project_receipt",
    "project_receipts",
]

__version__ = "0.1.5"
