import os
import pytest
from backend.api.kbase.models import Chunk
from backend.api.kbase.embedder_factory import get_embedder

@pytest.mark.asyncio
async def test_openai_integration_embed_text():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set; skipping OpenAI integration test.")
    openai_embedder = get_embedder("openai", api_key=api_key)
    
    chunk = Chunk(content="The quick brown fox jumps over the lazy dog.")
    embedded_chunk = await openai_embedder.embed_text(chunk)

   
    
    assert embedded_chunk.embeddings is not None
    assert isinstance(embedded_chunk.embeddings, list)
    assert len(embedded_chunk.embeddings) > 0
    assert all(isinstance(val, float) for val in embedded_chunk.embeddings)

@pytest.mark.asyncio
async def test_openai_integration_embed_query():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set; skipping OpenAI integration test.")
    openai_embedder = get_embedder("openai", api_key=api_key)
    
    query = "What is the meaning of life?"
    embedding = await openai_embedder.embed_query(query)


    
    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(val, float) for val in embedding)

@pytest.mark.asyncio
async def test_boto3_integration_embed_text():
    region_name = os.getenv("AWS_REGION")
    if not region_name:
        pytest.skip("AWS_REGION not set; skipping Boto3 integration test.")
    # Optionally, override model id via environment variable.
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-embed-text-v2:0")
    boto3_embedder = get_embedder("boto3", region_name=region_name, model_id=model_id)
    
    chunk = Chunk(content="Pack my box with five dozen liquor jugs.")
    embedded_chunk = await boto3_embedder.embed_text(chunk)


    
    assert embedded_chunk.embeddings is not None
    assert isinstance(embedded_chunk.embeddings, list)
    assert len(embedded_chunk.embeddings) > 0
    assert all(isinstance(val, float) for val in embedded_chunk.embeddings)

@pytest.mark.asyncio
async def test_boto3_integration_embed_query():
    region_name = os.getenv("AWS_REGION")
    if not region_name:
        pytest.skip("AWS_REGION not set; skipping Boto3 integration test.")
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-embed-text-v2:0")
    boto3_embedder = get_embedder("boto3", region_name=region_name, model_id=model_id)
    
    query = "How do I integrate AWS Bedrock?"
    embedding = await boto3_embedder.embed_query(query)


    
    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(val, float) for val in embedding)
