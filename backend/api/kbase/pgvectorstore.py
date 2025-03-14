import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.api.kbase.kbase_schema import KbaseDocumentORM
from backend.api.kbase.models import Document, Chunk, RetrievedChunks
from backend.api.kbase.math_helpers import mmr

class PostgresVectorStore:
    __slots__ = ("session", "kbase_id", "orm_model")
    def __init__(self, session: AsyncSession, kbase_id: uuid.UUID):
        """
        Args:
            session (AsyncSession): An async SQLAlchemy session.
            kbase_id (uuid.UUID): The knowledge base identifier. All documents added will be associated with this KB.
            orm_model (type): The ORM model class to use. Defaults to KbaseDocumentORM.
        """
        self.session = session
        self.kbase_id = kbase_id
        self.orm_model = KbaseDocumentORM

    async def add_document(self, document: Document) -> None:
        """
        Insert a document into the vector store.
        The document is a collection of chunks (each with an embedding).
        """
        orm_objects = []
        for chunk in document.chunks:
            if chunk.embeddings is None:
                raise ValueError("Chunk must have embeddings")
            orm_obj = self.orm_model(
                id=chunk.id,
                kbase_id=self.kbase_id,
                content=chunk.content,
                embedding=chunk.embeddings  # Uses the embedding dimension as defined in the schema.
            )
            orm_objects.append(orm_obj)
        self.session.add_all(orm_objects)
        await self.session.commit()

    async def similarity_search_by_vector(self, query_embedding: List[float], k: int = 4) -> RetrievedChunks:
        """
        Perform a similarity search using the vector distance operator (<->).
        Returns a RetrievedChunks object with the top k similar chunks.
        """
        stmt = (
            select(self.orm_model)
            .where(self.orm_model.kbase_id == self.kbase_id)
            .order_by(self.orm_model.embedding.op("<->")(query_embedding))
            .limit(k)
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        chunks = [
            Chunk(id=row.id, content=row.content, embeddings=row.embedding)
            for row in rows
        ]
        return RetrievedChunks(chunks=chunks)

    async def mmr_by_vector(self, query_embedding: List[float], k: int = 4, lambda_: float = 0.5) -> RetrievedChunks:
        """
        Perform a search using max marginal relevance (MMR) to re-rank the candidate documents.
        
        The method first retrieves a larger candidate set (10*k candidates), then uses the MMR formula
        to select k results that balance relevance and diversity.
        
        Args:
            query_embedding (List[float]): The query embedding.
            k (int): Number of documents to return.
            lambda_ (float): Trade-off parameter between relevance and diversity.
            
        Returns:
            RetrievedChunks: A Pydantic model containing a list of Chunk objects.
        """
        n_candidates = max(k * 10, k)
        stmt = (
            select(self.orm_model)
            .where(self.orm_model.kbase_id == self.kbase_id)
            .order_by(self.orm_model.embedding.op("<->")(query_embedding))
            .limit(n_candidates)
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        candidate_chunks = [Chunk(id=row.id, content=row.content, embeddings=row.embedding) for row in rows]
        candidate_vectors = [chunk.embeddings for chunk in candidate_chunks]
        
        selected_chunks = mmr(query_embedding, candidate_vectors, candidate_chunks, k, lambda_)
        return RetrievedChunks(chunks=selected_chunks)
