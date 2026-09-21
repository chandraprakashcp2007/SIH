"""
PRAHARI Copilot OpenAI-Compatible Provider Adapter
Communicates with OpenAI, Groq, or local Ollama endpoints via async HTTP.
"""
import httpx
import json
import logging
from typing import List, Dict, Any, AsyncGenerator, Optional
from backend.app.copilot.providers.base import LLMProvider
from backend.app.core.config import settings

logger = logging.getLogger("prahari.copilot.openai")


class OpenAICompatibleAdapter(LLMProvider):
    """Handles external API requests with strict timeouts and error isolation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 20.0
    ):
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = (base_url or settings.LLM_BASE_URL or "https://api.openai.com/v1").rstrip("/")
        self.model = model or settings.LLM_MODEL or "gpt-4o-mini"
        self.timeout_seconds = timeout_seconds

    def is_configured(self) -> bool:
        return bool(self.api_key or "localhost" in self.base_url or "127.0.0.1" in self.base_url)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        if not self.is_configured():
            raise ConnectionError("External LLM provider is not configured or missing API key.")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 800
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            msg = choice["message"]
            return {
                "content": msg.get("content") or "",
                "tool_calls": msg.get("tool_calls"),
                "provider": "OPENAI_COMPATIBLE",
                "model": self.model,
                "finish_reason": choice.get("finish_reason", "stop")
            }

    async def stream(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.1
    ) -> AsyncGenerator[str, None]:
        if not self.is_configured():
            raise ConnectionError("External LLM provider not configured.")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            "max_tokens": 800
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk_obj = json.loads(data_str)
                        delta = chunk_obj["choices"][0].get("delta", {})
                        content_piece = delta.get("content")
                        if content_piece:
                            yield content_piece
                    except Exception:
                        pass

    async def health_check(self) -> bool:
        if not self.is_configured():
            return False
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/models")
                return res.status_code in (200, 401)
        except Exception:
            return False
