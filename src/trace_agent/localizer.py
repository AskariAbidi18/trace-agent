from .models import FailureReport, ToolResult
from .tools import ToolSpec


class FailureLocalizer:
    """Maps observed execution evidence to a fine-grained failure category."""

    def localize(
        self,
        tool_name: str,
        arguments: dict,
        result: ToolResult,
        spec: ToolSpec | None,
    ) -> FailureReport:
        error = result.error or "Unknown tool failure"
        missing = []
        if spec:
            missing = [key for key in spec.required_arguments if key not in arguments]

        if missing:
            category = "invalid_tool_arguments"
            stage = "argument_validation"
        elif "ZeroDivisionError" in error:
            category = "tool_execution_error"
            stage = "tool_execution"
        elif "Unsupported expression" in error or "SyntaxError" in error:
            category = "invalid_tool_input"
            stage = "tool_execution"
        else:
            category = "tool_execution_error"
            stage = "tool_execution"

        evidence = {
            "tool_name": tool_name,
            "observed_arguments": arguments,
            "error_message": error,
            "required_arguments": spec.required_arguments if spec else [],
            "missing_arguments": missing,
        }
        return FailureReport(
            category=category,
            stage=stage,
            message=f"Failure localized to {stage}: {error}",
            evidence=evidence,
        )
