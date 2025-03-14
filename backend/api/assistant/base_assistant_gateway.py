from abc import ABC, abstractmethod
from typing import AsyncIterator
from backend.api.chat.models import ChatRequest

class BaseAssistantGateway(ABC):
    __slots__ = ()
    """ abstract base class with methods that all LLM gateways must implement """
    @abstractmethod
    async def get_ai_response_stream(self, chat_request: ChatRequest) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def get_summary_title(self, chat_request: ChatRequest) -> str:
        pass
