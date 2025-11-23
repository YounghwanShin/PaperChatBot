"""Gemini-based LLM client implementation."""

from typing import Optional
from google import genai
from google.genai import types

from ...core.exceptions import LLMError


class GeminiLLMClient:
    """Gemini API-based LLM client."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash",
        default_temperature: float = 0.1,
        default_max_tokens: int = 1024
    ):
        """Initialize Gemini LLM client.

        Args:
            api_key: Google API key
            model_name: Gemini model name
            default_temperature: Default sampling temperature
            default_max_tokens: Default maximum tokens
        """
        try:
            self.client = genai.Client(api_key=api_key)
            self.model_name = model_name
            self.default_temperature = default_temperature
            self.default_max_tokens = default_max_tokens
        except Exception as e:
            raise LLMError(f"Failed to initialize Gemini client: {e}")

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using Gemini API.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text

        Raises:
            LLMError: If generation fails
        """
        try:
            config = types.GenerateContentConfig(
                temperature=temperature if temperature is not None else self.default_temperature,
                max_output_tokens=max_tokens if max_tokens is not None else self.default_max_tokens,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            return response.text.strip()

        except Exception as e:
            raise LLMError(f"Text generation failed: {e}")
