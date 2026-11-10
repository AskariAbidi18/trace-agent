
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvidenceBundle:
    """A collection of execution evidence supporting failure diagnosis."""

    execution_id: str
    target_stage: str
    events: list[dict[str, Any]] = field(default_factory=list)
    relevant_tool_calls: list[dict[str, Any]] = field(default_factory=list)
    error_events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert the evidence bundle into a dictionary."""

        return {
            "execution_id": self.execution_id,
            "target_stage": self.target_stage,
            "event_count": len(self.events),
            "events": self.events,
            "relevant_tool_calls": self.relevant_tool_calls,
            "error_events": self.error_events,
        }


class EvidenceCollector:
    """Extracts relevant diagnostic evidence from execution traces."""

    def collect(
        self,
        events: list[dict[str, Any]],
        target_stage: str,
        execution_id: str,
    ) -> EvidenceBundle:
        """Build an evidence bundle for a particular execution stage."""

        stage_events = [
            event
            for event in events
            if (
                event.get("stage") == target_stage
                and event.get("execution_id") == execution_id
            )
        ]

        relevant_tool_calls = [
            event
            for event in stage_events
            if event.get("event_type") == "tool_call"
        ]

        error_events = [
            event
            for event in stage_events
            if event.get("severity") in {"ERROR", "CRITICAL"}
            or event.get("event_type") in {
                "tool_error",
                "execution_failure",
                "exception",
            }
        ]

        return EvidenceBundle(
            execution_id=execution_id,
            target_stage=target_stage,
            events=stage_events,
            relevant_tool_calls=relevant_tool_calls,
            error_events=error_events,
        )

    def collect_recent(
        self,
        events: list[dict[str, Any]],
        target_stage: str,
        execution_id: str,
        limit: int = 5,
    ) -> EvidenceBundle:
        """Collect only the most recent events from a specific stage."""

        if limit <= 0:
            raise ValueError("Evidence limit must be greater than zero.")

        bundle = self.collect(
            events=events,
            target_stage=target_stage,
            execution_id=execution_id,
        )

        bundle.events = bundle.events[-limit:]

        selected_ids = {
            event["event_id"]
            for event in bundle.events
        }

        bundle.relevant_tool_calls = [
            event
            for event in bundle.relevant_tool_calls
            if event["event_id"] in selected_ids
        ]

        bundle.error_events = [
            event
            for event in bundle.error_events
            if event["event_id"] in selected_ids
        ]

        return bundle
