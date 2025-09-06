import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# Needs to happen before local imports
os.environ["ENV_STATE"] = "test"

from src.app import app
from src.database.models import *  # To add to SQLModel metadata
from src.database.session import create_async_engine, get_session
from src.settings import get_database_config

db_config = get_database_config()
test_engine = create_async_engine(
    url=db_config["sqlalchemy.url"],
    echo=db_config["sqlalchemy.echo"],
    future=db_config["sqlalchemy.future"],
    connect_args=db_config.get("sqlalchemy.connect_args", {}),
)
AsyncSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def client() -> Generator:
    yield TestClient(app=app)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a fresh transactional session for each test.
    Rolls back after test completes.
    """
    async with AsyncSessionLocal() as session:
        async with session.begin_nested():  # Begin a nested transaction
            yield session
            await session.rollback()  # Roll back everything after test


@pytest.fixture
def override_get_session(db_session):
    """
    Override get_session dependency so endpoints use the transactional test session.
    """

    async def _override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def truncate_tables():
    """
    Need to truncate and reset identities after every test due to nested transactions
    """
    async with test_engine.begin() as conn:
        yield
        await conn.execute(
            text(
                """
                TRUNCATE TABLE pipeline, pipeline_type, pipeline_execution
                RESTART IDENTITY CASCADE
                """
            )
        )


@pytest.fixture(scope="session", autouse=True)
async def setup_teardown():
    try:
        async with test_engine.begin() as conn:
            await conn.execute(text("DROP TYPE IF EXISTS datepartenum"))
            await conn.run_sync(SQLModel.metadata.create_all)

        yield
    finally:
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.execute(text("DROP TYPE IF EXISTS datepartenum"))


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac
