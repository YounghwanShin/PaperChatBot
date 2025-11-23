"""Protocol for LLM clients."""

from typing import Protocol, Optional


class LLMClientProtocol(Protocol):
    """Interface for LLM clients."""

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text from prompt.

        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        ...
