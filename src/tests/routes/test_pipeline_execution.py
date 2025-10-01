import pytest
from httpx import AsyncClient
from sqlmodel import select

from src.database.models.pipeline_execution import PipelineExecutionClosure
from src.database.pipeline_execution_utils import (
    db_maintain_pipeline_execution_closure_table,
)
from src.tests.conftest import AsyncSessionLocal
from src.tests.fixtures.pipeline import TEST_PIPELINE_POST_DATA
from src.tests.fixtures.pipeline_execution import (
    TEST_PIPELINE_EXECUTION_END_DATA,
    TEST_PIPELINE_EXECUTION_START_DATA,
)


@pytest.mark.anyio
async def test_start_and_end_pipeline_execution(async_client: AsyncClient):
    await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    response = await async_client.post(
        "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
    )
    assert response.status_code == 201
    assert response.json() == {"id": 1}

    response = await async_client.post(
        "/end_pipeline_execution", json=TEST_PIPELINE_EXECUTION_END_DATA
    )
    assert response.status_code == 204


@pytest.mark.anyio
async def test_dml_updates_pipeline(async_client: AsyncClient):
    await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    response = await async_client.post(
        "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
    )
    assert response.status_code == 201
    assert response.json() == {"id": 1}

    response = await async_client.post(
        "/end_pipeline_execution", json=TEST_PIPELINE_EXECUTION_END_DATA
    )
    assert response.status_code == 204

    response = await async_client.get("/pipeline")
    data = response.json()[0]

    assert data["last_target_insert"] is not None
    assert data["last_target_update"] is not None
    assert data["last_target_soft_delete"] is not None


@pytest.mark.anyio
async def test_pipeline_execution_closure_table(
    async_client: AsyncClient, mock_celery_tasks
):
    """Test that pipeline execution closure table is properly maintained"""

    # Create a pipeline
    await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)

    # Create parent execution
    parent_data = TEST_PIPELINE_EXECUTION_START_DATA.copy()
    parent_response = await async_client.post(
        "/start_pipeline_execution", json=parent_data
    )
    assert parent_response.status_code == 201
    parent_id = parent_response.json()["id"]

    # Manually trigger closure table maintenance for parent
    async with AsyncSessionLocal() as session:
        await db_maintain_pipeline_execution_closure_table(session, parent_id, None)

    # Create child execution with parent_id
    child_data = TEST_PIPELINE_EXECUTION_START_DATA.copy()
    child_data["parent_id"] = parent_id
    child_response = await async_client.post(
        "/start_pipeline_execution", json=child_data
    )
    assert child_response.status_code == 201
    child_id = child_response.json()["id"]

    # Manually trigger closure table maintenance for child
    async with AsyncSessionLocal() as session:
        await db_maintain_pipeline_execution_closure_table(session, child_id, parent_id)

    # Check closure table entries
    async with AsyncSessionLocal() as session:
        # Check parent self-reference (depth 0)
        parent_self_query = select(PipelineExecutionClosure).where(
            PipelineExecutionClosure.parent_execution_id == parent_id,
            PipelineExecutionClosure.child_execution_id == parent_id,
            PipelineExecutionClosure.depth == 0,
        )
        parent_self = await session.exec(parent_self_query)
        parent_self_result = parent_self.first()
        assert parent_self_result is not None

        # Check child self-reference (depth 0)
        child_self_query = select(PipelineExecutionClosure).where(
            PipelineExecutionClosure.parent_execution_id == child_id,
            PipelineExecutionClosure.child_execution_id == child_id,
            PipelineExecutionClosure.depth == 0,
        )
        child_self = await session.exec(child_self_query)
        child_self_result = child_self.first()
        assert child_self_result is not None

        # Check parent-child relationship (depth 1)
        parent_child_query = select(PipelineExecutionClosure).where(
            PipelineExecutionClosure.parent_execution_id == parent_id,
            PipelineExecutionClosure.child_execution_id == child_id,
            PipelineExecutionClosure.depth == 1,
        )
        parent_child = await session.exec(parent_child_query)
        parent_child_result = parent_child.first()
        assert parent_child_result is not None
