import argparse
import json

from .agent import TraceAgent
from .llm import MockProvider, OllamaProvider
from .tools import build_default_registry
from .trace import TraceRecorder


def main():
    parser = argparse.ArgumentParser(description="Run the TRACE tool-augmented agent.")
    parser.add_argument("--provider", choices=["mock", "ollama"], default="mock")
    parser.add_argument("--model", default="qwen2.5:3b")
    parser.add_argument("--task", default="Calculate 125 multiplied by 4.")
    args = parser.parse_args()

    provider = (
        OllamaProvider(model=args.model)
        if args.provider == "ollama"
        else MockProvider()
    )
    agent = TraceAgent(
        provider=provider,
        tools=build_default_registry(),
        recorder=TraceRecorder("data/trace.jsonl"),
    )
    result = agent.run(args.task)
    print(json.dumps(result.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    main()
