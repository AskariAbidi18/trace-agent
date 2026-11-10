# TRACE Agent

**Tool Runtime Auditing, Classification and Evidence-grounded Recovery Engine**

TRACE is a research prototype that adds fine-grained monitoring, failure localization, evidence collection, and bounded recovery to tool-augmented LLM agents.

## Current MVP scope

- A small tool registry with a calculator tool.
- Structured execution traces in JSONL format.
- Failure classification for invalid arguments, tool execution errors, and malformed agent output.
- Evidence-grounded recovery with bounded retries.
- Ollama provider support and a deterministic mock provider for repeatable tests.
- Fault injection to demonstrate a recoverable tool-call failure.

## Architecture

```text
User Task
   |
   v
LLM Agent -----> Tool Registry -----> Tool Execution
   |                                      |
   |                                      v
   |                                Trace Recorder
   |                                      |
   |                              Failure Localizer
   |                                      |
   |                              Evidence Collector
   |                                      |
   +<---------------- Recovery Engine <---+
   |
   v
Final Response
```

## Setup

Python 3.10+ is required.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"
```

### Run with the deterministic demo

```bash
python run_demo.py
```

The demo injects a missing tool argument on the first attempt. TRACE records the failure, diagnoses it, restores the argument from the original call evidence, retries once, and verifies the result.

### Run with Ollama

Install Ollama, then pull the model:

```bash
ollama pull qwen2.5:3b
```

Start Ollama and run:

```bash
python -m trace_agent.cli --provider ollama --model qwen2.5:3b
```

The local provider uses Ollama's `/api/chat` endpoint. The default endpoint is `http://localhost:11434`.

## Tests

```bash
pytest
```

## Important research boundary

The current implementation is an MVP scaffold, not a validated research result. Fault injection is a controlled demonstration mechanism. Evaluation against naturally occurring agent failures, baseline comparisons, and broader tool coverage are future milestones.
