import uuid
import pytest
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from backend.api.kbase.models import Document, Chunk, RetrievedChunks
from backend.api.kbase.pgvectorstore import PostgresVectorStore
from backend.api.kbase.kbase_schema import Base, KbaseDocumentORM

# Helper to generate a dummy vector of length 1536.
def dummy_vector(value: float) -> List[float]:
    return [value] * 1536

@pytest.mark.asyncio
async def test_add_document_and_similarity_search(async_session: AsyncSession):
    """
    Test adding a Document (with chunks) into the vector store and then performing
    a similarity search.
    """
    # Create a random kbase_id (in production this would come from a KnowledgeBase record)
    kbase_id = uuid.uuid4()
    vector_store = PostgresVectorStore(
        session=async_session,
        kbase_id=kbase_id
    )

    # Create a document with two chunks:
    # Chunk A has a dummy embedding of all 0.0 and Chunk B has all 1.0.
    chunk_a = Chunk(
        id=uuid.uuid4(),
        content="Document A",
        embeddings=dummy_vector(0.0)
    )
    chunk_b = Chunk(
        id=uuid.uuid4(),
        content="Document B",
        embeddings=dummy_vector(1.0)
    )
    document = Document(chunks=[chunk_a, chunk_b])

    # Add the document to the vector store.
    await vector_store.add_document(document)

    # Prepare a query embedding that is closer to [0.0]*1536.
    query_embedding = dummy_vector(0.05)

    # Run similarity search.
    retrieved: RetrievedChunks = await vector_store.similarity_search_by_vector(query_embedding, k=2)
    assert retrieved is not None
    assert isinstance(retrieved.chunks, list)
    # Expect the most similar chunk to be "Document A"
    similar_contents = [chunk.content for chunk in retrieved.chunks]
    assert "Document A" in similar_contents

    # Cleanup: delete inserted rows based on kbase_id.
    await async_session.execute(delete(KbaseDocumentORM).where(KbaseDocumentORM.kbase_id == kbase_id))
    await async_session.commit()

@pytest.mark.asyncio
async def test_mmr_search(async_session: AsyncSession):
    """
    Test the mmr_by_vector method of the vector store.
    (For now, mmr_by_vector is a simple alias to similarity_search_by_vector.)
    """
    # Create a random kbase_id.
    kbase_id = uuid.uuid4()
    vector_store = PostgresVectorStore(
        session=async_session,
        kbase_id=kbase_id
    )

    # Create a document with two chunks having distinct dummy embeddings.
    chunk_x = Chunk(
        id=uuid.uuid4(),
        content="Doc X",
        embeddings=dummy_vector(0.3)
    )
    chunk_y = Chunk(
        id=uuid.uuid4(),
        content="Doc Y",
        embeddings=dummy_vector(0.7)
    )
    document = Document(chunks=[chunk_x, chunk_y])
    await vector_store.add_document(document)

    # Use a query embedding that is in between 0.3 and 0.7.
    query_embedding = dummy_vector(0.5)
    retrieved: RetrievedChunks = await vector_store.mmr_by_vector(query_embedding, k=2)
    assert retrieved is not None
    assert len(retrieved.chunks) == 2
    # Check that each retrieved chunk has a valid embedding (list of floats of length 1536).
    for chunk in retrieved.chunks:
        assert isinstance(chunk.embeddings, list)
        assert len(chunk.embeddings) == 1536
        assert all(isinstance(val, float) for val in chunk.embeddings)

    # Cleanup: delete inserted rows based on kbase_id.
    await async_session.execute(delete(KbaseDocumentORM).where(KbaseDocumentORM.kbase_id == kbase_id))
    await async_session.commit()
