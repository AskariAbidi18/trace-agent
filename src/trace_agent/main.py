
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from trace_agent.core.agent import TRACEAgent
from trace_agent.llm.ollama import OllamaLLM
from trace_agent.tools.registry import ToolRegistry


# Tool registration
registry = ToolRegistry()

registry.register(
    "add",
    lambda x, y: x + y,
    "Adds two numbers. Arguments: x and y.",
)

# Initialize the TRACE agent once
agent = TRACEAgent(
    llm=OllamaLLM(model="qwen2.5:3b"),
    registry=registry,
)

app = FastAPI(
    title="TRACE API",
    description="Failure localization and evidence-grounded recovery in tool-augmented LLM agents.",
    version="0.1.0",
)

# Allow local frontend development servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task: str = Field(min_length=1, max_length=2000)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "TRACE API",
        "model": "qwen2.5:3b",
    }


@app.post("/api/run")
def run_task(request: TaskRequest):
    task = request.task.strip()

    if not task:
        raise HTTPException(
            status_code=400,
            detail="Task cannot be empty.",
        )

    try:
        result = agent.run(task)

        return {
            "success": result.success,
            "task": result.task,
            "answer": result.answer,
            "attempts": result.attempts,
            "execution_time_ms": result.execution_time_ms,
            "trace": result.trace,
            "failure_reports": [
                failure.to_dict()
                for failure in result.failure_reports
            ],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"TRACE execution failed: {exc}",
        ) from exc
