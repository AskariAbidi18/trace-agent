from copy import deepcopy
from .models import FailureReport
from .tools import ToolSpec


class RecoveryEngine:
    """
    Performs conservative, evidence-grounded repairs.
    It only restores a required argument when its value is present in the
    original tool-call record. It does not invent missing values.
    """

    def repair_arguments(
        self,
        observed_arguments: dict,
        original_arguments: dict,
        report: FailureReport,
        spec: ToolSpec,
    ) -> tuple[dict | None, str]:
        repaired = deepcopy(observed_arguments)

        if report.category == "invalid_tool_arguments":
            for key in report.evidence.get("missing_arguments", []):
                if key in original_arguments:
                    repaired[key] = original_arguments[key]

            still_missing = [
                key for key in spec.required_arguments if key not in repaired
            ]
            if not still_missing:
                return repaired, (
                    "Restored missing required argument(s) using the original "
                    "tool-call record and tool schema."
                )

        return None, (
            "No safe repair could be derived from the available execution evidence."
        )
