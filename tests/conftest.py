import asyncio
import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Test database URL for in-memory SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create a test database engine
# NullPool is used because SQLite in-memory DBs don't persist across connections typically,
# and it avoids issues with event loops and connection sharing in tests.
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool, # Important for SQLite in-memory with asyncio
)

# Create a test session factory, bound to the test_engine
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False, # Standard for FastAPI to keep objects accessible
    autocommit=False,       # We will control transactions explicitly
    autoflush=False,        # We will control flushing explicitly
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for a test, with a clean database schema."""
    # Create all tables for the test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Yield the session for the test to use
    async with TestSessionLocal() as session:
        yield session
    
    # Drop all tables after the test is done to ensure isolation
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Create a FastAPI TestClient that uses the test database session."""
    
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        """Override for the get_db dependency to use the test session."""
        yield db_session
    
    # Apply the dependency override
    app.dependency_overrides[get_db] = override_get_db
    
    # Yield the test client for the test to use
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear the dependency overrides after the test is done
    app.dependency_overrides.clear()