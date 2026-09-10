"""
Database Engine & Async Session Configuration
Supports async SQLite for MVP and seamless transition to async PostgreSQL/PostGIS.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Engine configuration with appropriate connection arguments
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session per request.
    Rolls back transaction on uncaught exceptions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Synchronous engine and session for sync operations and Module 2 endpoints
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+aiosqlite", "")
sync_connect_args = {}
if SYNC_DATABASE_URL.startswith("sqlite"):
    sync_connect_args["check_same_thread"] = False

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    connect_args=sync_connect_args
)

SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


def get_sync_db():
    """
    FastAPI dependency yielding a synchronous session for sync-compatible endpoints.
    """
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

