
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class ToolResult:
    """Represents the outcome of a tool execution."""

    tool_name: str
    success: bool
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FailureReport:
    """Stores a localized failure and its supporting evidence."""

    failure_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    category: str = "unknown"
    stage: str = "unknown"
    message: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)
    recovery_suggestion: str | None = None
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert the failure report into a serializable dictionary."""

        return {
            "failure_id": self.failure_id,
            "category": self.category,
            "stage": self.stage,
            "message": self.message,
            "evidence": self.evidence,
            "recovery_suggestion": self.recovery_suggestion,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class AgentResult:
    """Represents the final result of an agent execution."""

    success: bool
    task: str
    answer: str | None = None
    attempts: int = 0
    trace: list[dict[str, Any]] = field(default_factory=list)
    failure_reports: list[FailureReport] = field(
        default_factory=list
    )
    execution_time_ms: float = 0.0
