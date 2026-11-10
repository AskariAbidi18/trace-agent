from trace_agent.agent import TraceAgent
from trace_agent.llm import MockProvider
from trace_agent.tools import build_default_registry
from trace_agent.trace import TraceRecorder


def test_agent_recovers_from_missing_argument(tmp_path):
    def inject(tool_name, arguments, attempt):
        if attempt == 1:
            return {}
        return arguments

    agent = TraceAgent(
        provider=MockProvider(),
        tools=build_default_registry(),
        recorder=TraceRecorder(str(tmp_path / "trace.jsonl")),
        max_retries=1,
        fault_injector=inject,
    )
    result = agent.run("Calculate 125 multiplied by 4.")

    assert result.success is True
    assert result.attempts == 2
    assert result.answer == "The result is 500."
    assert result.failure_reports[0].category == "invalid_tool_arguments"


def test_agent_stops_after_retry_limit(tmp_path):
    def always_break(tool_name, arguments, attempt):
        return {}

    agent = TraceAgent(
        provider=MockProvider(),
        tools=build_default_registry(),
        recorder=TraceRecorder(str(tmp_path / "trace.jsonl")),
        max_retries=1,
        fault_injector=always_break,
    )
    result = agent.run("Calculate 125 multiplied by 4.")

    assert result.success is False
    assert result.attempts == 2
