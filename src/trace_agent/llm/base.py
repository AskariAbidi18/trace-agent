
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class GenerationConfig:
    """Configuration options for language model generation."""

    temperature: float = 0.2
    max_tokens: int = 1024
    top_p: float = 0.9

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature must be between 0 and 2.")

        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero.")

        if not 0.0 < self.top_p <= 1.0:
            raise ValueError("top_p must be greater than 0 and at most 1.")


class BaseLLM(ABC):
    """Provider-independent interface for language models."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        config: GenerationConfig | None = None,
    ) -> str:
        """Generate a text response from the language model."""
        raise NotImplementedError
