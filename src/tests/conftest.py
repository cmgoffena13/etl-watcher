import os

# Needs to happen before local imports
os.environ["ENV_STATE"] = "test"
from typing import AsyncGenerator, Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app import app
from src.database.models import *  # To add to SQLModel metadata
from src.database.session import create_async_engine, get_session
from src.settings import config, get_database_config

db_config = get_database_config()
test_engine = create_async_engine(
    url=db_config["sqlalchemy.url"],
    echo=False,  # Disable echo for tests
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
    Truncate tables after each test for clean state
    """
    yield
    try:
        async with test_engine.begin() as conn:
            await conn.execute(
                text(
                    """
                    TRUNCATE TABLE 
                    anomaly_detection_result,
                    anomaly_detection_rule,
                    timeliness_pipeline_execution_log,
                    pipeline_execution,
                    address_lineage_closure,
                    address_lineage,
                    pipeline,
                    address,
                    pipeline_type,
                    address_type
                    RESTART IDENTITY CASCADE
                    """
                )
            )
    except Exception as e:
        # If truncation fails, log the error but don't fail the test
        print(f"Warning: Failed to truncate tables: {e}")


@pytest.fixture(scope="session", autouse=True)
async def setup_teardown():
    try:
        async with test_engine.begin() as conn:
            await conn.execute(text("DROP TYPE IF EXISTS datepartenum"))
            await conn.execute(text("DROP TYPE IF EXISTS anomalymetricfieldenum"))
            await conn.execute(text("DROP TYPE IF EXISTS timelinessdatepartenum"))
            await conn.execute(
                text("DROP MATERIALIZED VIEW IF EXISTS daily_pipeline_report")
            )
            await conn.run_sync(SQLModel.metadata.create_all)

        yield

    finally:
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.execute(text("DROP TYPE IF EXISTS datepartenum"))
            await conn.execute(text("DROP TYPE IF EXISTS anomalymetricfieldenum"))
            await conn.execute(text("DROP TYPE IF EXISTS timelinessdatepartenum"))
            await conn.execute(
                text("DROP MATERIALIZED VIEW IF EXISTS daily_pipeline_report")
            )

        # Properly dispose of the engine to close all connections
        await test_engine.dispose()


@pytest.fixture(autouse=True)
def mock_slack_notifications():
    """Mock all Slack notifications globally to avoid setup in each test"""
    mock_send_slack_message = Mock()

    import src.database.anomaly_detection_utils
    import src.database.freshness_utils
    import src.database.timeliness_utils
    import src.notifier

    src.notifier.send_slack_message = mock_send_slack_message
    src.database.timeliness_utils.send_slack_message = mock_send_slack_message
    src.database.anomaly_detection_utils.send_slack_message = mock_send_slack_message
    src.database.freshness_utils.send_slack_message = mock_send_slack_message

    yield mock_send_slack_message


@pytest.fixture(autouse=True)
def mock_background_tasks():
    """Mock background tasks globally to prevent them from executing during tests"""
    mock_add_task = Mock()

    # Mock FastAPI's BackgroundTasks.add_task method
    from fastapi import BackgroundTasks

    BackgroundTasks.add_task = mock_add_task

    yield {"add_task": mock_add_task}


@pytest.fixture(autouse=True)
def mock_celery_tasks():
    """Mock Celery tasks globally to prevent them from executing during tests"""
    mock_delay = Mock()
    mock_delay.return_value.id = "test-task-id"

    # Mock the delay method on all Celery tasks
    from celery import Task

    Task.delay = mock_delay

    yield mock_delay


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac
