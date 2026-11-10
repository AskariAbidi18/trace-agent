
from dataclasses import dataclass
from enum import Enum


class FailureCategory(str, Enum):
    """Standardized failure categories supported by TRACE."""

    PLANNING_FAILURE = "planning_failure"
    TOOL_SELECTION_FAILURE = "tool_selection_failure"
    ARGUMENT_GENERATION_FAILURE = "argument_generation_failure"
    TOOL_EXECUTION_FAILURE = "tool_execution_failure"
    OUTPUT_INTERPRETATION_FAILURE = "output_interpretation_failure"
    VERIFICATION_FAILURE = "verification_failure"


class FailureStage(str, Enum):
    """Execution stages where failures can originate."""

    PLANNING = "planning"
    TOOL_SELECTION = "tool_selection"
    ARGUMENT_GENERATION = "argument_generation"
    TOOL_EXECUTION = "tool_execution"
    OUTPUT_INTERPRETATION = "output_interpretation"
    VERIFICATION = "verification"


@dataclass(frozen=True)
class FailureDefinition:
    """Metadata describing a recognized failure category."""

    category: FailureCategory
    stage: FailureStage
    description: str
    recovery_strategy: str


FAILURE_TAXONOMY = {
    FailureCategory.PLANNING_FAILURE: FailureDefinition(
        category=FailureCategory.PLANNING_FAILURE,
        stage=FailureStage.PLANNING,
        description=(
            "The agent generates an incorrect, incomplete, "
            "or logically inconsistent execution plan."
        ),
        recovery_strategy="replan_task",
    ),

    FailureCategory.TOOL_SELECTION_FAILURE: FailureDefinition(
        category=FailureCategory.TOOL_SELECTION_FAILURE,
        stage=FailureStage.TOOL_SELECTION,
        description=(
            "The agent selects an unavailable or inappropriate "
            "tool for the requested operation."
        ),
        recovery_strategy="select_alternative_tool",
    ),

    FailureCategory.ARGUMENT_GENERATION_FAILURE: FailureDefinition(
        category=FailureCategory.ARGUMENT_GENERATION_FAILURE,
        stage=FailureStage.ARGUMENT_GENERATION,
        description=(
            "The agent generates missing, invalid, or incorrectly "
            "formatted arguments for a tool invocation."
        ),
        recovery_strategy="repair_tool_arguments",
    ),

    FailureCategory.TOOL_EXECUTION_FAILURE: FailureDefinition(
        category=FailureCategory.TOOL_EXECUTION_FAILURE,
        stage=FailureStage.TOOL_EXECUTION,
        description=(
            "A selected tool encounters an exception, timeout, "
            "or unsuccessful execution."
        ),
        recovery_strategy="retry_tool_execution",
    ),

    FailureCategory.OUTPUT_INTERPRETATION_FAILURE: FailureDefinition(
        category=FailureCategory.OUTPUT_INTERPRETATION_FAILURE,
        stage=FailureStage.OUTPUT_INTERPRETATION,
        description=(
            "The agent incorrectly interprets or extracts "
            "information from a tool's returned output."
        ),
        recovery_strategy="reinterpret_tool_output",
    ),

    FailureCategory.VERIFICATION_FAILURE: FailureDefinition(
        category=FailureCategory.VERIFICATION_FAILURE,
        stage=FailureStage.VERIFICATION,
        description=(
            "The agent incorrectly validates the result or "
            "fails to detect an inconsistent final response."
        ),
        recovery_strategy="revalidate_result",
    ),
}


def get_failure_definition(
    category: FailureCategory | str,
) -> FailureDefinition:
    """Retrieve metadata for a recognized failure category."""

    try:
        normalized_category = FailureCategory(category)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported failure category: {category}"
        ) from exc

    return FAILURE_TAXONOMY[normalized_category]
