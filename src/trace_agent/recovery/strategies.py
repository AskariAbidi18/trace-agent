
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from trace_agent.diagnosis.taxonomy import FailureCategory
from trace_agent.core.models import FailureReport


@dataclass
class RecoveryContext:
    """Contains information required to execute a recovery strategy."""

    failure: FailureReport
    original_input: dict[str, Any] = field(default_factory=dict)
    available_tools: list[str] = field(default_factory=list)
    previous_attempts: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryResult:
    """Represents the outcome of a recovery strategy."""

    success: bool
    strategy: str
    repaired_input: dict[str, Any] | None = None
    explanation: str = ""
    requires_llm: bool = False


class RecoveryStrategy(ABC):
    """Base interface for all recovery strategies."""

    @abstractmethod
    def recover(self, context: RecoveryContext) -> RecoveryResult:
        pass


class ReplanStrategy(RecoveryStrategy):
    def recover(self, context: RecoveryContext) -> RecoveryResult:
        return RecoveryResult(
            success=False,
            strategy="replan_task",
            explanation="Task replanning requires LLM-assisted reasoning.",
            requires_llm=True,
        )


class ToolSelectionStrategy(RecoveryStrategy):
    def recover(self, context: RecoveryContext) -> RecoveryResult:
        failed_tool = context.original_input.get("tool")

        alternatives = [
            tool
            for tool in context.available_tools
            if tool != failed_tool
        ]

        if not alternatives:
            return RecoveryResult(
                success=False,
                strategy="select_alternative_tool",
                explanation="No alternative tools are available.",
            )

        return RecoveryResult(
            success=True,
            strategy="select_alternative_tool",
            repaired_input={"candidate_tools": alternatives},
            explanation="Alternative tools identified for selection.",
            requires_llm=True,
        )


class ArgumentRepairStrategy(RecoveryStrategy):
    def recover(self, context: RecoveryContext) -> RecoveryResult:
        arguments = context.original_input.get("arguments", {})
        required = context.metadata.get("required_arguments", [])

        if not isinstance(arguments, dict):
            return RecoveryResult(
                success=False,
                strategy="repair_tool_arguments",
                explanation="Tool arguments must be a dictionary.",
            )

        missing = [
            name for name in required
            if name not in arguments
        ]

        recovered = {
            name: context.metadata["original_arguments"][name]
            for name in missing
            if name in context.metadata.get("original_arguments", {})
        }

        if any(name not in recovered for name in missing):
            return RecoveryResult(
                success=False,
                strategy="repair_tool_arguments",
                explanation=(
                    "Some required arguments cannot be recovered "
                    "from the available evidence."
                ),
            )

        repaired_arguments = {**arguments, **recovered}

        return RecoveryResult(
            success=True,
            strategy="repair_tool_arguments",
            repaired_input={"arguments": repaired_arguments},
            explanation="Missing arguments restored from original execution evidence.",
        )


class ToolRetryStrategy(RecoveryStrategy):
    def recover(self, context: RecoveryContext) -> RecoveryResult:
        if context.previous_attempts >= 1:
            return RecoveryResult(
                success=False,
                strategy="retry_tool_execution",
                explanation="Retry limit reached.",
            )

        return RecoveryResult(
            success=True,
            strategy="retry_tool_execution",
            repaired_input=context.original_input,
            explanation="A bounded retry has been authorized.",
        )


class OutputInterpretationStrategy(RecoveryStrategy):
    def recover(self, context: RecoveryContext) -> RecoveryResult:
        return RecoveryResult(
            success=False,
            strategy="reinterpret_tool_output",
            explanation="Output reinterpretation requires LLM-assisted reasoning.",
            requires_llm=True,
        )


class VerificationStrategy(RecoveryStrategy):
    def recover(self, context: RecoveryContext) -> RecoveryResult:
        return RecoveryResult(
            success=True,
            strategy="revalidate_result",
            repaired_input=context.original_input,
            explanation="Result requires independent revalidation.",
        )


RECOVERY_STRATEGIES = {
    FailureCategory.PLANNING_FAILURE: ReplanStrategy(),
    FailureCategory.TOOL_SELECTION_FAILURE: ToolSelectionStrategy(),
    FailureCategory.ARGUMENT_GENERATION_FAILURE: ArgumentRepairStrategy(),
    FailureCategory.TOOL_EXECUTION_FAILURE: ToolRetryStrategy(),
    FailureCategory.OUTPUT_INTERPRETATION_FAILURE: OutputInterpretationStrategy(),
    FailureCategory.VERIFICATION_FAILURE: VerificationStrategy(),
}


def get_recovery_strategy(
    category: FailureCategory | str,
) -> RecoveryStrategy:
    """Retrieve the recovery strategy associated with a failure category."""

    try:
        normalized = FailureCategory(category)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported recovery category: {category}"
        ) from exc

    return RECOVERY_STRATEGIES[normalized]
