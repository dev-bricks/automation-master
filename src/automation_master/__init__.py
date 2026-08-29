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
from .runtime import (
    AutomationRuntime,
    RuntimeReceiptConflictError,
    RuntimeReceiptStore,
    build_runtime_receipt,
    read_provider_receipt,
    read_scheduler_run,
)
from .service import AutomationMaster, BudgetState, CreditPolicy, ReceiptMetrics
from .store import EventConflictError, EventStore

__all__ = [
    "AutomationMaster",
    "AutomationRuntime",
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
    "RuntimeReceiptConflictError",
    "RuntimeReceiptStore",
    "ReceiptRetentionClass",
    "ReceiptRetentionPolicy",
    "RunClass",
    "AntigravityPromptRepairContractAdapter",
    "PromptRepairContractAdapter",
    "PromptRepairContractError",
    "PromptRepairContractResult",
    "project_receipt",
    "project_receipts",
    "build_runtime_receipt",
    "read_provider_receipt",
    "read_scheduler_run",
]

__version__ = "0.1.1"
