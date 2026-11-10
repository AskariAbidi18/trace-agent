
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


class ExecutionTracer:
    """Records structured events throughout an agent execution."""

    def __init__(
        self,
        execution_id: str,
        log_directory: str = "data/traces",
    ):
        self.execution_id = execution_id
        self.log_directory = Path(log_directory)

        self.log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.log_file = (
            self.log_directory / f"{execution_id}.jsonl"
        )

        self.events: list[dict[str, Any]] = []

    def record(
        self,
        event_type: str,
        stage: str,
        details: dict[str, Any] | None = None,
        severity: str = "INFO",
    ) -> dict[str, Any]:
        """Record an event and persist it to the execution log."""

        event = {
            "event_id": str(uuid4()),
            "execution_id": self.execution_id,
            "event_type": event_type,
            "stage": stage,
            "severity": severity,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "details": details or {},
        }

        self.events.append(event)

        with self.log_file.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                json.dumps(
                    event,
                    ensure_ascii=False,
                    default=str,
                ) + "\n"
            )

        return event

    def get_events(self) -> list[dict[str, Any]]:
        """Return all events recorded in the current execution."""

        return list(self.events)

    def get_events_by_stage(
        self,
        stage: str,
    ) -> list[dict[str, Any]]:
        """Retrieve events associated with a specific stage."""

        return [
            event
            for event in self.events
            if event["stage"] == stage
        ]

    def get_events_by_type(
        self,
        event_type: str,
    ) -> list[dict[str, Any]]:
        """Retrieve events of a particular type."""

        return [
            event
            for event in self.events
            if event["event_type"] == event_type
        ]
