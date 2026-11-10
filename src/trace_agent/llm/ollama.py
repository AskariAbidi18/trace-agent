import json
import urllib.error
import urllib.request


class OllamaProvider:
    def __init__(
        self,
        model: str = "qwen2.5:3b",
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate_json(self, prompt: str) -> dict:
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {
                    "role": "system",
                    "content": "Return only valid JSON. Follow the requested schema exactly.",
                },
                {"role": "user", "content": prompt},
            ],
        }
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data["message"]["content"]
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                raise ValueError("LLM response must be a JSON object.")
            return parsed
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Could not reach Ollama. Is Ollama running and the model downloaded?"
            ) from exc
        except (KeyError, json.JSONDecodeError) as exc:
            raise RuntimeError("Ollama returned an invalid JSON response.") from exc
