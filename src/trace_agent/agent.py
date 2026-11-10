from typing import Callable

from .localizer import FailureLocalizer
from .models import AgentResult
from .recovery import RecoveryEngine
from .tools import ToolRegistry
from .trace import TraceRecorder


class TraceAgent:
    def __init__(
        self,
        provider,
        tools: ToolRegistry,
        recorder: TraceRecorder | None = None,
        max_retries: int = 1,
        fault_injector: Callable | None = None,
    ):
        self.provider = provider
        self.tools = tools
        self.recorder = recorder or TraceRecorder()
        self.max_retries = max_retries
        self.fault_injector = fault_injector
        self.localizer = FailureLocalizer()
        self.recovery = RecoveryEngine()

    def run(self, task: str) -> AgentResult:
        self.recorder.record("task_received", task=task)
        plan_prompt = (
            "Choose a tool to complete the task. Return JSON with keys "
            "'tool' and 'arguments'. Available tools: "
            f"{self.tools.schemas()}. Task: {task}"
        )
        self.recorder.record("planning_started", prompt=plan_prompt)
        plan = self.provider.generate_json(plan_prompt)

        tool_name = plan.get("tool")
        original_arguments = plan.get("arguments", {})
        if not isinstance(original_arguments, dict) or not tool_name:
            report = {
                "category": "malformed_agent_output",
                "stage": "planning",
                "message": "The LLM did not return a valid tool and argument object.",
            }
            self.recorder.record("failure_localized", **report)
            return AgentResult(False, task, report["message"], 0, self.recorder.events)

        try:
            spec = self.tools.get(tool_name)
        except KeyError as exc:
            self.recorder.record(
                "failure_localized",
                category="tool_selection_failure",
                stage="tool_selection",
                error=str(exc),
            )
            return AgentResult(False, task, str(exc), 0, self.recorder.events)

        observed_arguments = dict(original_arguments)
        attempts = 0
        failure_reports = []

        while attempts <= self.max_retries:
            attempts += 1
            current_arguments = dict(observed_arguments)
            if self.fault_injector:
                current_arguments = self.fault_injector(
                    tool_name, current_arguments, attempts
                )

            self.recorder.record(
                "tool_call",
                attempt=attempts,
                tool=tool_name,
                arguments=current_arguments,
            )
            result = self.tools.execute(tool_name, current_arguments)
            self.recorder.record(
                "tool_result",
                attempt=attempts,
                tool=tool_name,
                success=result.success,
                output=result.output,
                error=result.error,
                duration_ms=result.duration_ms,
            )

            if result.success:
                final_prompt = (
                    "Produce the final answer as JSON with key 'answer'. "
                    f"Task: {task}. Tool result: {result.output}"
                )
                final = self.provider.generate_json(final_prompt)
                answer = str(final.get("answer", result.output))
                self.recorder.record(
                    "task_completed", answer=answer, attempts=attempts
                )
                return AgentResult(
                    True, task, answer, attempts, self.recorder.events, failure_reports
                )

            report = self.localizer.localize(
                tool_name, current_arguments, result, spec
            )
            failure_reports.append(report)
            self.recorder.record(
                "failure_localized",
                category=report.category,
                stage=report.stage,
                message=report.message,
                evidence=report.evidence,
            )

            repaired, rationale = self.recovery.repair_arguments(
                current_arguments, original_arguments, report, spec
            )
            self.recorder.record(
                "recovery_attempt",
                attempt=attempts,
                repaired_arguments=repaired,
                rationale=rationale,
            )
            if repaired is None or attempts > self.max_retries:
                break
            observed_arguments = repaired

        self.recorder.record("task_failed", attempts=attempts)
        return AgentResult(
            False,
            task,
            "Task could not be completed safely within the retry limit.",
            attempts,
            self.recorder.events,
            failure_reports,
        )
