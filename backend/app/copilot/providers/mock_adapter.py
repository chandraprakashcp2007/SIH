"""
PRAHARI Copilot Mock Provider Adapter
Used for offline unit tests and deterministic CI test suites.
"""
from typing import List, Dict, Any, AsyncGenerator, Optional
from backend.app.copilot.providers.base import LLMProvider


class MockProvider(LLMProvider):
    """Predictable mock provider for test verification."""

    def __init__(self, mock_reply: str = "Mock grounded intelligence response."):
        self.mock_reply = mock_reply
        self.should_fail = False

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        if self.should_fail:
            raise ConnectionError("Simulated mock provider network failure.")
        return {
            "content": self.mock_reply,
            "provider": "MOCK",
            "model": "mock-model-v1",
            "finish_reason": "stop"
        }

    async def stream(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.1
    ) -> AsyncGenerator[str, None]:
        if self.should_fail:
            raise ConnectionError("Simulated mock stream failure.")
        words = self.mock_reply.split(" ")
        for w in words:
            yield w + " "

    async def health_check(self) -> bool:
        return not self.should_fail
