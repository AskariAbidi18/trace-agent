
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from trace_agent.core.models import FailureReport
from trace_agent.recovery.strategies import (
    RecoveryContext,
    RecoveryResult,
    get_recovery_strategy,
)


@dataclass
class RecoveryDecision:
    """Records the decision made by the recovery engine."""

    decision_id: str
    failure_id: str
    category: str
    strategy: str
    success: bool
    explanation: str
    requires_llm: bool
    timestamp: str


class RecoveryEngine:
    """Coordinates recovery strategies based on localized failures."""

    def __init__(self):
        self.decisions: list[RecoveryDecision] = []

    def execute(
        self,
        failure: FailureReport,
        original_input: dict[str, Any] | None = None,
        available_tools: list[str] | None = None,
        previous_attempts: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> RecoveryResult:
        """Select and execute the appropriate recovery strategy."""

        if previous_attempts < 0:
            raise ValueError("Previous attempts cannot be negative.")

        context = RecoveryContext(
            failure=failure,
            original_input=original_input or {},
            available_tools=available_tools or [],
            previous_attempts=previous_attempts,
            metadata=metadata or {},
        )

        strategy = get_recovery_strategy(failure.category)
        result = strategy.recover(context)

        decision = RecoveryDecision(
            decision_id=str(uuid4()),
            failure_id=failure.failure_id,
            category=failure.category,
            strategy=result.strategy,
            success=result.success,
            explanation=result.explanation,
            requires_llm=result.requires_llm,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self.decisions.append(decision)

        return result

    def get_decisions(self) -> list[dict[str, Any]]:
        """Return the history of recovery decisions."""

        return [
            asdict(decision)
            for decision in self.decisions
        ]

    def get_decisions_by_failure(
        self,
        failure_id: str,
    ) -> list[dict[str, Any]]:
        """Retrieve all recovery decisions for a specific failure."""

        return [
            asdict(decision)
            for decision in self.decisions
            if decision.failure_id == failure_id
        ]
