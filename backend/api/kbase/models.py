from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class Chunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    content: str
    embeddings: Optional[List[float]] = None
    metadata: Optional[dict] = None

class Document(BaseModel):
    chunks: List[Chunk]

class RetrievedChunks(BaseModel):
    chunks: List[Chunk]

class KnowledgeBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    account_short_code: Optional[str] = None
    
    # Change from 'date' to 'datetime'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeBaseList(BaseModel):
    kbases: List[KnowledgeBase]