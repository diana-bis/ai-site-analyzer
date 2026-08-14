import hashlib
from abc import ABC, abstractmethod

# Base interface for any LLM implementation (real or mock)
class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Generate a text response for the given prompt."""


class MockLLMClient(LLMClient):
    """Mock implementation that returns deterministic responses.
    The same prompt always produces the same output, making
    testing predictable without calling a real LLM API."""

    _TEMPLATES = [
        "Based on the available information: {excerpt}",
        "Analysis suggests the following: {excerpt}",
        "The most likely explanation is: {excerpt}",
    ]

    def complete(self, prompt: str) -> str:
        # Generate a deterministic seed from the prompt
        seed = int(hashlib.sha256(prompt.encode()).hexdigest(), 16)

        # Select one of the templates based on the seed
        template = self._TEMPLATES[seed % len(self._TEMPLATES)]

        return template.format(excerpt=self._excerpt(prompt))

    def _excerpt(self, prompt: str) -> str:
        # Drop whichever trailing part isn't failure data - the raw
        # response body (cause prompts) or the instruction sentence
        # (narrative prompts) - so the excerpt never echoes a raw dict or
        # gets truncated mid-word/mid-JSON.
        content = prompt.split(". Actual result:")[0]
        content = content.split("Summarize what these failures mean together")[0].strip()

        if len(content) <= 200:
            return content
        return content[:200].rsplit(" ", 1)[0] + "..."
