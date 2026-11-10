class MockProvider:
    """Deterministic provider used for tests and reproducible demonstrations."""

    def generate_json(self, prompt: str) -> dict:
        if "Choose a tool" in prompt:
            return {
                "tool": "calculator",
                "arguments": {"expression": "125 * 4"},
            }
        if "Produce the final answer" in prompt:
            return {"answer": "The result is 500."}
        return {}
