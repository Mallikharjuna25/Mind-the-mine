"""
Pytest Fixtures & Test Client Setup
Configures isolated in-memory async SQLite engine and test HTTP client.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base, get_db
from app.core.security import create_access_token, UserRole
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "test-user-admin-01", "email": "admin@mineguard.in", "role": UserRole.SUPER_ADMIN})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def token_headers(auth_headers):
    return auth_headers


@pytest.fixture
def safety_officer_headers():
    token = create_access_token(data={"sub": "test-safety-officer-01", "email": "safety@mineguard.in", "role": UserRole.SAFETY_OFFICER})
    return {"Authorization": f"Bearer {token}"}

