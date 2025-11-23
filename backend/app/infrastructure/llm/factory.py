"""Factory for creating LLM clients."""

from ...core.interfaces import LLMClientProtocol
from .gemini import GeminiLLMClient


def create_llm_client(
    api_key: str,
    model_name: str = "gemini-2.0-flash",
    temperature: float = 0.1,
    max_tokens: int = 1024
) -> LLMClientProtocol:
    """Create an LLM client instance.

    Args:
        api_key: API key for the LLM service
        model_name: Model name
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        LLM client instance
    """
    return GeminiLLMClient(
        api_key=api_key,
        model_name=model_name,
        default_temperature=temperature,
        default_max_tokens=max_tokens
    )
