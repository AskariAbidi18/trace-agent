
import json
import time
from typing import Any

from trace_agent.core.models import AgentResult
from trace_agent.core.state import AgentState, ExecutionStage
from trace_agent.diagnosis.localizer import FailureLocalizer
from trace_agent.llm.base import BaseLLM
from trace_agent.monitoring.evidence import EvidenceCollector
from trace_agent.monitoring.tracer import ExecutionTracer
from trace_agent.recovery.engine import RecoveryEngine
from trace_agent.tools.executor import ToolExecutor
from trace_agent.tools.registry import ToolRegistry


class TRACEAgent:
    """Tool-augmented agent with failure localization and recovery."""

    def __init__(
        self,
        llm: BaseLLM,
        registry: ToolRegistry,
        log_directory: str = "data/traces",
    ) -> None:
        self.llm = llm
        self.registry = registry
        self.executor = ToolExecutor(registry)
        self.evidence_collector = EvidenceCollector()
        self.localizer = FailureLocalizer()
        self.recovery_engine = RecoveryEngine()
        self.log_directory = log_directory

    @staticmethod
    def _parse_plan(response: str) -> dict[str, Any]:
        """Extract a JSON tool plan from the LLM response."""

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}")

            if start == -1 or end <= start:
                raise ValueError("LLM did not return a valid JSON plan.")

            try:
                return json.loads(response[start:end + 1])
            except json.JSONDecodeError as exc:
                raise ValueError("LLM returned malformed JSON.") from exc

    def run(self, task: str) -> AgentResult:
        """Plan, execute, diagnose, recover and produce an answer."""

        start_time = time.perf_counter()
        state = AgentState(task=task)
        state.start()

        tracer = ExecutionTracer(
            execution_id=state.execution_id,
            log_directory=self.log_directory,
        )

        failure_reports = []

        try:
            tracer.record(
                "task_started",
                "initialization",
                {"task": task},
            )

            state.update_stage(ExecutionStage.PLANNING)

            tool_descriptions = self.registry.describe()

            planning_prompt = f"""
You are the planning component of TRACE, a tool-using agent.

User task:
{task}

Available tools:
{json.dumps(tool_descriptions)}

Return ONLY a JSON object in this format:
{{
    "tool": "tool_name",
    "arguments": {{"argument_name": "value"}}
}}

Choose one appropriate tool. Do not invent tools.
"""

            plan_response = self.llm.generate(planning_prompt)
            plan = self._parse_plan(plan_response)

            tool_name = plan.get("tool")
            arguments = plan.get("arguments", {})

            if not isinstance(tool_name, str) or not tool_name:
                raise ValueError("Plan does not contain a valid tool name.")

            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be a JSON object.")

            state.update_stage(ExecutionStage.TOOL_SELECTION)

            tracer.record(
                "tool_selected",
                "tool_selection",
                {"tool_name": tool_name},
            )

            state.update_stage(ExecutionStage.ARGUMENT_GENERATION)

            tracer.record(
                "arguments_generated",
                "argument_generation",
                {"arguments": arguments},
            )

            state.update_stage(ExecutionStage.TOOL_EXECUTION)
            state.record_tool_call(tool_name, arguments)

            tracer.record(
                "tool_call",
                "tool_execution",
                {
                    "tool_name": tool_name,
                    "arguments": arguments,
                },
            )

            result = self.executor.execute(tool_name, arguments)

            tracer.record(
                "tool_success" if result.success else "tool_error",
                "tool_execution",
                {
                    "tool_name": tool_name,
                    "output": result.output,
                    "error": result.error,
                    "duration_ms": result.duration_ms,
                },
                severity="INFO" if result.success else "ERROR",
            )

            if not result.success:
                evidence = self.evidence_collector.collect(
                    tracer.get_events(),
                    "tool_execution",
                    state.execution_id,
                )

                failure_event = tracer.get_events()[-1]

                failure = self.localizer.localize(
                    failure_event,
                    evidence,
                )

                failure_reports.append(failure)
                state.record_failure(failure)

                tracer.record(
                    "failure_localized",
                    "tool_execution",
                    failure.to_dict(),
                    severity="WARNING",
                )

                recovery = self.recovery_engine.execute(
                    failure,
                    original_input={
                        "tool": tool_name,
                        "arguments": arguments,
                    },
                    previous_attempts=0,
                )

                tracer.record(
                    "recovery_decision",
                    "recovery",
                    {
                        "strategy": recovery.strategy,
                        "success": recovery.success,
                        "explanation": recovery.explanation,
                    },
                )

                if recovery.success and recovery.strategy == "retry_tool_execution":
                    state.record_recovery_attempt()

                    result = self.executor.execute(
                        tool_name,
                        arguments,
                    )

                    tracer.record(
                        "tool_success" if result.success else "tool_error",
                        "tool_execution",
                        {
                            "tool_name": tool_name,
                            "output": result.output,
                            "error": result.error,
                            "retry": True,
                        },
                        severity="INFO" if result.success else "ERROR",
                    )

            if not result.success:
                state.fail()

                return AgentResult(
                    success=False,
                    task=task,
                    attempts=2 if failure_reports else 1,
                    trace=tracer.get_events(),
                    failure_reports=failure_reports,
                    execution_time_ms=(
                        time.perf_counter() - start_time
                    ) * 1000,
                )

            state.update_stage(ExecutionStage.OUTPUT_INTERPRETATION)

            answer = self.llm.generate(
                prompt=(
                    f"User task: {task}\n"
                    f"Tool used: {tool_name}\n"
                    f"Tool output: {result.output}\n\n"
                    "Explain the tool result accurately and concisely. "
                    "Do not invent information."
                ),
                system_prompt="You are a precise assistant. Use the supplied tool output as evidence.",
            )

            tracer.record(
                "answer_generated",
                "output_interpretation",
                {"answer": answer},
            )

            state.complete()

            tracer.record(
                "task_completed",
                "completed",
                {"success": True},
            )

            return AgentResult(
                success=True,
                task=task,
                answer=answer,
                attempts=2 if failure_reports else 1,
                trace=tracer.get_events(),
                failure_reports=failure_reports,
                execution_time_ms=(
                    time.perf_counter() - start_time
                ) * 1000,
            )

        except Exception as exc:
            state.fail()

            tracer.record(
                "execution_failure",
                state.current_stage.value,
                {
                    "exception_type": type(exc).__name__,
                    "error": str(exc),
                },
                severity="ERROR",
            )

            return AgentResult(
                success=False,
                task=task,
                attempts=1,
                trace=tracer.get_events(),
                failure_reports=failure_reports,
                execution_time_ms=(
                    time.perf_counter() - start_time
                ) * 1000,
            )
