from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0


@dataclass
class FailureReport:
    category: str
    stage: str
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    success: bool
    task: str
    answer: str
    attempts: int
    trace: list[dict[str, Any]]
    failure_reports: list[FailureReport] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        return result
