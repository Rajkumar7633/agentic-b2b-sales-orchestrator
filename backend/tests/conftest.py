import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.agents.init_agents import initialize_agents
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    initialize_agents()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Admin JWT headers for tests."""
    token = create_access_token({
        "sub": "usr_admin_001",
        "email": "admin@nexora.ai",
        "role": "ADMIN",
        "tenant_id": "tenant_nexora_default"
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sales_rep_headers():
    """Sales Rep JWT headers (limited permissions)."""
    token = create_access_token({
        "sub": "usr_rep_001",
        "email": "rep@nexora.ai",
        "role": "SALES_REP",
        "tenant_id": "tenant_nexora_default"
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def reviewer_headers():
    """Reviewer JWT headers."""
    token = create_access_token({
        "sub": "usr_reviewer_001",
        "email": "reviewer@nexora.ai",
        "role": "REVIEWER",
        "tenant_id": "tenant_nexora_default"
    })
    return {"Authorization": f"Bearer {token}"}
