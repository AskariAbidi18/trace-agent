
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from .models import FailureReport


class ExecutionStage(str, Enum):
    INITIALIZATION = "initialization"
    PLANNING = "planning"
    TOOL_SELECTION = "tool_selection"
    ARGUMENT_GENERATION = "argument_generation"
    TOOL_EXECUTION = "tool_execution"
    OUTPUT_INTERPRETATION = "output_interpretation"
    VERIFICATION = "verification"
    RECOVERY = "recovery"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    RECOVERING = "recovering"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentState:
    task: str
    execution_id: str = field(default_factory=lambda: str(uuid4()))

    current_stage: ExecutionStage = ExecutionStage.INITIALIZATION
    status: ExecutionStatus = ExecutionStatus.PENDING

    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    failures: list[FailureReport] = field(default_factory=list)
    recovery_attempts: int = 0

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def update_stage(self, stage: ExecutionStage) -> None:
        """Update the active execution stage."""

        self.current_stage = stage
        self.updated_at = datetime.now(timezone.utc)

    def start(self) -> None:
        """Mark execution as started."""

        self.status = ExecutionStatus.RUNNING
        self.update_stage(ExecutionStage.PLANNING)

    def record_tool_call(self, tool_name: str, arguments: dict) -> None:
        """Record a tool invocation."""

        self.tool_calls.append({
            "tool_name": tool_name,
            "arguments": arguments,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        self.updated_at = datetime.now(timezone.utc)

    def record_failure(self, failure: FailureReport) -> None:
        """Attach a failure report to the current execution."""

        self.failures.append(failure)
        self.status = ExecutionStatus.RECOVERING
        self.updated_at = datetime.now(timezone.utc)

    def record_recovery_attempt(self) -> None:
        """Increment the recovery attempt counter."""

        self.recovery_attempts += 1
        self.status = ExecutionStatus.RECOVERING
        self.update_stage(ExecutionStage.RECOVERY)

    def complete(self) -> None:
        """Mark execution as successfully completed."""

        self.status = ExecutionStatus.COMPLETED
        self.update_stage(ExecutionStage.COMPLETED)

    def fail(self) -> None:
        """Mark execution as unsuccessful."""

        self.status = ExecutionStatus.FAILED
        self.update_stage(ExecutionStage.FAILED)
