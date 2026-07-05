from typing import Protocol


class LLMPort(Protocol):
    def generate(self, prompt: str, model: str = "qwen2.5:3b") -> str:
        """
        Envía un prompt al LLM y devuelve la respuesta en texto plano.
        La implementación concreta hablará con Ollama vía HTTP.
        """
        ...
