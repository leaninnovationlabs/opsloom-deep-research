import uuid
from sqlalchemy import Column, String, Boolean, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class AssistantORM(Base):
    __tablename__ = "assistant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    account_short_code = Column(String, nullable=True)
    kbase_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String(100), nullable=False)
    config = Column(JSON, nullable=True)
    system_prompts = Column(JSON, nullable=True)
    assistant_metadata = Column(JSON, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
