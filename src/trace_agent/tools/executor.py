
import time
from typing import Any

from trace_agent.core.models import ToolResult
from trace_agent.tools.registry import ToolRegistry


class ToolExecutor:
    """Executes registered tools and captures their outcomes."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> ToolResult:
        """Execute a tool and return its structured result."""

        if arguments is None:
            arguments = {}

        if not isinstance(arguments, dict):
            raise TypeError("Tool arguments must be provided as a dictionary.")

        try:
            tool = self.registry.get(tool_name)
        except KeyError as exc:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=str(exc),
                metadata={"failure_type": "tool_not_found"},
            )

        start_time = time.perf_counter()

        try:
            output = tool(**arguments)
            duration_ms = (time.perf_counter() - start_time) * 1000

            return ToolResult(
                tool_name=tool_name,
                success=True,
                output=output,
                duration_ms=duration_ms,
            )

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000

            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
                duration_ms=duration_ms,
                metadata={
                    "failure_type": "tool_execution_error",
                    "exception_type": type(exc).__name__,
                },
            )
