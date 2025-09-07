import pytest
from httpx import AsyncClient

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
