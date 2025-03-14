import pytest
import pytest_asyncio 
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "postgresql+asyncpg://myuser:mypassword@localhost:5432/ragdb"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)



@pytest.fixture(autouse=True)
def force_engine_dispose():
    """Dispose of the shared engine at the end of each test."""
    yield

    async def async_dispose():
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session():
    """
    Provide an async SQLAlchemy session for database tests,
    using an async fixture so it yields a real AsyncSession object.
    """
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    try:                                                                                                                                                                    
        async with async_session_factory() as session:                                                                                                                      
            yield session                                                                                                                                                   
    finally:                                                                                                                                                                
        await engine.dispose()