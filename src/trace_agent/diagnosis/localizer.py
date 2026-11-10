
from typing import Any

from trace_agent.core.models import FailureReport
from trace_agent.diagnosis.taxonomy import (
    FailureCategory,
    FailureStage,
    get_failure_definition,
)
from trace_agent.monitoring.evidence import EvidenceBundle


STAGE_CATEGORY_MAP = {
    FailureStage.PLANNING.value: FailureCategory.PLANNING_FAILURE,
    FailureStage.TOOL_SELECTION.value: FailureCategory.TOOL_SELECTION_FAILURE,
    FailureStage.ARGUMENT_GENERATION.value: FailureCategory.ARGUMENT_GENERATION_FAILURE,
    FailureStage.TOOL_EXECUTION.value: FailureCategory.TOOL_EXECUTION_FAILURE,
    FailureStage.OUTPUT_INTERPRETATION.value: FailureCategory.OUTPUT_INTERPRETATION_FAILURE,
    FailureStage.VERIFICATION.value: FailureCategory.VERIFICATION_FAILURE,
}

FAILURE_EVENT_TYPES = {
    "tool_error",
    "execution_failure",
    "exception",
    "validation_failure",
    "planning_failure",
    "tool_selection_failure",
    "argument_generation_failure",
    "interpretation_failure",
    "verification_failure",
}


class FailureLocalizer:
    """Localizes execution failures using observed events and evidence."""

    def localize(
        self,
        failure_event: dict[str, Any],
        evidence: EvidenceBundle,
    ) -> FailureReport:
        """Generate a structured diagnosis from a failure event."""

        if not isinstance(failure_event, dict):
            raise TypeError("Failure event must be a dictionary.")

        execution_id = failure_event.get("execution_id")
        event_id = failure_event.get("event_id")
        event_type = failure_event.get("event_type")
        stage = failure_event.get("stage")
        severity = failure_event.get("severity", "").upper()

        if execution_id != evidence.execution_id:
            raise ValueError(
                "Failure event and evidence bundle belong to different executions."
            )

        if not event_id:
            raise ValueError("Failure event must contain an event ID.")

        if not event_type:
            raise ValueError("Failure event must contain an event type.")

        if not stage:
            raise ValueError("Failure event must contain an execution stage.")

        is_failure = (
            severity in {"ERROR", "CRITICAL"}
            or event_type in FAILURE_EVENT_TYPES
        )

        if not is_failure:
            raise ValueError(
                "The supplied event does not contain a recognized failure signal."
            )

        if stage != evidence.target_stage:
            raise ValueError(
                "Failure stage does not match the evidence bundle target stage."
            )

        category = STAGE_CATEGORY_MAP.get(stage)

        if category is None:
            raise ValueError(
                f"Cannot localize an unsupported execution stage: {stage}"
            )

        definition = get_failure_definition(category)

        supporting_events = [
            event
            for event in evidence.events
            if event.get("execution_id") == execution_id
        ]

        if event_id not in {
            event.get("event_id") for event in supporting_events
        }:
            raise ValueError(
                "Failure event is not present in the supplied evidence bundle."
            )

        observed_details = failure_event.get("details", {})

        evidence_data = {
            "execution_id": execution_id,
            "failure_event_id": event_id,
            "event_type": event_type,
            "severity": severity,
            "observed_details": observed_details,
            "supporting_event_ids": [
                event.get("event_id")
                for event in supporting_events
            ],
            "relevant_tool_calls": evidence.relevant_tool_calls,
            "error_events": evidence.error_events,
            "diagnostic_method": "deterministic_stage_mapping",
            "root_cause_status": "not_established",
        }

        message = (
            f"Failure localized to stage '{stage}' and classified as "
            f"'{category.value}'. {definition.description}"
        )

        return FailureReport(
            category=category.value,
            stage=stage,
            message=message,
            evidence=evidence_data,
            recovery_suggestion=definition.recovery_strategy,
        )
