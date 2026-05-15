import logging
from typing import Any, Optional

import httpx

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.chat_endpoint = f"{self.base_url}/api/chat"
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.embeddings_endpoint = f"{self.base_url}/api/embeddings"

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> dict[str, Any]:
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(self.chat_endpoint, json=payload)
            response.raise_for_status()
            return response.json()

    async def generate(
        self,
        model: str,
        prompt: str,
        stream: bool = False,
        **kwargs
    ) -> dict[str, Any]:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            **kwargs
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(self.generate_endpoint, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_embeddings(self, model: str, text: str) -> list[float]:
        payload = {"model": model, "prompt": text}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.embeddings_endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])


_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient(base_url=settings.ollama_base_url)
    return _ollama_client
