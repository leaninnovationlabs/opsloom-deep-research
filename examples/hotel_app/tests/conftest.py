import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base
from backend.db.db_init import initialize_database

# Create a separate in-memory SQLite engine for tests
# Each test gets its own database
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
    future=True,
    connect_args={"check_same_thread": False}
)

test_async_session_maker = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

@pytest_asyncio.fixture
async def async_session():
    """
    Create a fresh database for each test.
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed the database with test data
    await initialize_database()
    
    # Create a session for the test
    async with test_async_session_maker() as session:
        yield session
    
    # Clean up after the test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)