import asyncio
from backend.api.kbase.models import Chunk
from backend.api.kbase.base_embedder_gateway import BaseEmbedderGateway
from openai import OpenAI  # New client class

class OpenAIEmbedderGateway(BaseEmbedderGateway):
    def __init__(self, api_key: str, model: str = "text-embedding-3-large"):
        self.api_key = api_key
        self.model = model
        # Instantiate the new OpenAI client with the API key.
        self.client = OpenAI(api_key=self.api_key)

    async def embed_text(self, chunk: Chunk) -> Chunk:
        embedding = await asyncio.to_thread(self._get_embedding, chunk.content)
        chunk.embeddings = embedding
        return chunk

    async def embed_query(self, query: str) -> list[float]:
        embedding = await asyncio.to_thread(self._get_embedding, query)
        return embedding

    def _get_embedding(self, text: str) -> list[float]:
        # Use the new client syntax and access attributes instead of subscripting.
        response = self.client.embeddings.create(input=[text], model=self.model)
        embedding = response.data[0].embedding  # Dot notation access
        return embedding
