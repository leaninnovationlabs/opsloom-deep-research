from abc import ABC, abstractmethod
from backend.api.kbase.models import Chunk

class BaseEmbedderGateway(ABC):
    __slots__ = ()
    """ abstract base class with methods that all embedder classes must implement """
    @abstractmethod
    async def embed_text(self, chunk: Chunk) -> Chunk:
        """ embed text. adds embeddings to Chunk object """
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> list[float]:
        """ embed query """
        pass