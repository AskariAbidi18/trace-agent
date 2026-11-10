import json
import time
from pathlib import Path
from typing import Any


class TraceRecorder:
    """Stores append-only JSONL events so every decision is auditable."""

    def __init__(self, path: str = "trace.jsonl"):
        self.path = Path(path)
        self.events: list[dict[str, Any]] = []

    def record(self, event_type: str, **payload: Any) -> dict[str, Any]:
        event = {
            "event_id": len(self.events) + 1,
            "timestamp": time.time(),
            "event_type": event_type,
            **payload,
        }
        self.events.append(event)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, default=str) + "\\n")
        return event
