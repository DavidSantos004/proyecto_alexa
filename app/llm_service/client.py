import os

import httpx

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self._base_url = base_url

    def generate(self, prompt: str, model: str = "qwen2.5:3b") -> str:
        response = httpx.post(
            f"{self._base_url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
