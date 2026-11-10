
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from trace_agent.llm.base import BaseLLM, GenerationConfig


class OllamaError(Exception):
    """Raised when communication with Ollama fails."""


class OllamaLLM(BaseLLM):
    """Ollama implementation of the BaseLLM interface."""

    def __init__(
        self,
        model: str = "qwen2.5:3b",
        host: str = "http://localhost:11434",
        timeout: int = 120,
    ) -> None:
        if not model.strip():
            raise ValueError("Model name cannot be empty.")

        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")

        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        config: GenerationConfig | None = None,
    ) -> str:
        """Generate a response using the Ollama API."""

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        config = config or GenerationConfig()

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "num_predict": config.max_tokens,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        request = Request(
            url=f"{self.host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_data = json.loads(
                    response.read().decode("utf-8")
                )

        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise OllamaError(
                f"Ollama returned HTTP {exc.code}: {error_body}"
            ) from exc

        except URLError as exc:
            raise OllamaError(
                f"Could not connect to Ollama at {self.host}: {exc.reason}"
            ) from exc

        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise OllamaError(
                "Ollama returned an invalid response."
            ) from exc

        generated_text = response_data.get("response")

        if not isinstance(generated_text, str):
            raise OllamaError(
                "Ollama response did not contain valid generated text."
            )

        return generated_text.strip()
