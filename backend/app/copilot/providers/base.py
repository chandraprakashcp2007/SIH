"""
PRAHARI Copilot LLM Provider Interface
Abstract base class defining contract for online and offline model adapters.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Optional


class LLMProvider(ABC):
    """Abstract model provider interface."""

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Generate text or tool calls synchronously."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.1
    ) -> AsyncGenerator[str, None]:
        """Stream token chunks asynchronously."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify provider availability and network connectivity."""
        pass

    def is_configured(self) -> bool:
        """Check if provider has valid credentials/endpoints."""
        return True
