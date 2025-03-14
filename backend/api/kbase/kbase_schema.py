import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Text
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class KnowledgeBaseORM(Base):
    __tablename__ = "kbase"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    account_short_code = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class KbaseDocumentORM(Base):
    __tablename__ = "kbase_documents"
    
    # Primary key and foreign key to the KnowledgeBase table
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kbase_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content = Column(Text, nullable=False)
    # For production, set the dimension to the expected value (e.g. 1536)
    # openai text-large is 3072
    # bedrock text is 1024
    embedding = Column(Vector, nullable=False)