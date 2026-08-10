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

        # Use the last line of the prompt as the response excerpt
        excerpt = prompt.strip().splitlines()[-1][:200]
        
        return template.format(excerpt=excerpt)
