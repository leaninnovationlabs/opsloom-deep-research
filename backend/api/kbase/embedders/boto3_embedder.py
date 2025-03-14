import json
import boto3
import asyncio
from backend.api.kbase.models import Chunk
from backend.api.kbase.base_embedder_gateway import BaseEmbedderGateway

class Boto3EmbedderGateway(BaseEmbedderGateway):
    def __init__(self, region_name: str, model_id: str = "amazon.titan-embed-text-v2:0"):
        self.region_name = region_name
        self.model_id = model_id
        # Initialize the boto3 client for Bedrock Runtime.
        self.client = boto3.client("bedrock-runtime", region_name=self.region_name)

    async def embed_text(self, chunk: Chunk) -> Chunk:
        embedding = await asyncio.to_thread(self._get_embedding, chunk.content)
        chunk.embeddings = embedding
        return chunk

    async def embed_query(self, query: str) -> list[float]:
        embedding = await asyncio.to_thread(self._get_embedding, query)
        return embedding

    def _get_embedding(self, text: str) -> list[float]:
        # Note: Use the expected key "inputText" per the model's JSON schema.
        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            body=json.dumps({"inputText": text}).encode("utf-8")
        )
        result = json.loads(response["body"].read())
        return result.get("embedding", [])
