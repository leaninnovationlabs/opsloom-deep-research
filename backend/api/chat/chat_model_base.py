import os
from abc import ABC, abstractmethod
from typing import List, AsyncIterator, Iterator, Optional, TypedDict, Literal
from backend.api.chat.models import OpsLoomMessageChunk
from typing_extensions import NotRequired

# Abstract base class defining the chat-model interface.
class BaseChatModel(ABC):
    @abstractmethod
    def invoke(self, messages: List[str]) -> OpsLoomMessageChunk:
        """
        Synchronously send a list of messages (e.g. conversation history or a single prompt)
        to the chat model and return the full result as an OpsLoomMessageChunk.
        """
        pass

    @abstractmethod 
    def embed_query(self, query: str) -> List[float]:
        """
        Generate an embedding for the given query.
        """
        pass

    @abstractmethod
    def stream(self, messages: List[str]) -> Iterator[OpsLoomMessageChunk]:
        """
        Synchronously stream a response from the chat model, yielding OpsLoomMessageChunk items.
        """
        pass

    @abstractmethod
    async def ainvoke(self, messages: List[str]) -> OpsLoomMessageChunk:
        """
        Asynchronously send a list of messages to the chat model and return the full result.
        """
        pass

    @abstractmethod
    async def astream(self, messages: List[str]) -> AsyncIterator[OpsLoomMessageChunk]:
        """
        Asynchronously stream a response from the chat model, yielding OpsLoomMessageChunk items.
        """
        pass