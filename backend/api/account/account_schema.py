import uuid
from sqlalchemy import Column, String, DateTime, Boolean, JSON, CHAR, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AccountORM(Base):
    __tablename__ = "account"

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    short_code = Column(String(10), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    password = Column(CHAR(60), nullable=True)
    protection = Column(String(255), nullable=False, default='none')

    # rename the column so it won't clash with Base.metadata
    account_metadata = Column(JSON, nullable=True)

    root = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
