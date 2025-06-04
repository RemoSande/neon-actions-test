# SQLAlchemy & FastAPI specific imports for async database operations.
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# Application-specific settings (e.g., database_url).
from app.core.config import settings
# FastAPI's dependency injection.
from fastapi import Depends
# Type hinting.
from typing import Annotated, AsyncGenerator

# ===== Database Engine =====
# The engine is the entry point to the database.
engine = create_async_engine(
    settings.database_url,  # Database connection string from settings
    echo=settings.database_echo, # Log SQL statements (for debugging)
    future=True, # Use modern SQLAlchemy features
)

# ===== Session Factory =====
# Creates new database session instances.
AsyncSessionLocal = async_sessionmaker(
    engine,                 # Bind to our engine
    class_=AsyncSession,    # Use AsyncSession for sessions
    expire_on_commit=False, # Keep objects accessible after commit
    autocommit=False,       # Manual commit control
    autoflush=False,        # Manual flush control
)

# ===== Database Session Dependency for FastAPI =====
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to provide a DB session per request."""
    # Create a new session for this request.
    # `async with` ensures the session is always closed.
    async with AsyncSessionLocal() as session:
        try:
            # Provide the session to the route handler.
            # Execution pauses here until the route handler finishes.
            yield session
            # If the route handler was successful, commit changes.
            await session.commit()
        except Exception:
            # If any error occurred, roll back changes.
            await session.rollback()
            raise # Re-raise error for FastAPI to handle
        finally:
            # Always close the session to free resources.
            await session.close()

# ===== Type Hint for Injected DB Session =====
# `DbSession` is used in route handlers to get a session via `Depends(get_db)`.
DbSession = Annotated[AsyncSession, Depends(get_db)]
# --- End of File ---
# Add a blank line at the end if there isn't one, as per PEP 8 (Python style guide).





