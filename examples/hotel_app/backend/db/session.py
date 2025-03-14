import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Use in-memory SQLite - data exists only during the application lifetime
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create a single engine instance that will be shared for the app lifetime
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  
    future=True,
    # This is needed for SQLite to work with multiple threads
    connect_args={"check_same_thread": False}
)

# Create a single sessionmaker instance
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an AsyncSession.
    Yields the session, ensuring that it is closed after use.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()