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


@pytest.fixture(scope="session", autouse=True)
def override_get_session():
    """
    Override the get_session function that is required for all routes.
    Ensures sessions in routes are pointed at Test database instead of Dev/Prod.
    """

    async def _override() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
async def setup_teardown():
    try:
        async with test_engine.begin() as conn:
            print(SQLModel.metadata.tables.keys())
            for tname, table in SQLModel.metadata.tables.items():
                for col in table.columns:
                    if hasattr(col.type, "enums"):  # Enum columns
                        print(col.name, col.type.enums)
            # await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            # await conn.execute(text("DROP TABLE IF EXISTS pipeline_execution"))
            # await conn.execute(text("DROP TABLE IF EXISTS pipeline"))
            # await conn.execute(text("DROP TABLE IF EXISTS pipeline_type"))
            await conn.execute(text("DROP TYPE IF EXISTS datepartenum CASCADE"))
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
