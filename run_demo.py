import json

from trace_agent.agent import TraceAgent
from trace_agent.llm import MockProvider
from trace_agent.tools import build_default_registry
from trace_agent.trace import TraceRecorder


def inject_missing_expression(tool_name, arguments, attempt):
    # Controlled fault: simulate an argument being lost before tool execution.
    if tool_name == "calculator" and attempt == 1:
        return {}
    return arguments


if __name__ == "__main__":
    agent = TraceAgent(
        provider=MockProvider(),
        tools=build_default_registry(),
        recorder=TraceRecorder("data/demo_trace.jsonl"),
        max_retries=1,
        fault_injector=inject_missing_expression,
    )
    result = agent.run("Calculate 125 multiplied by 4.")
    print(json.dumps(result.to_dict(), indent=2, default=str))
