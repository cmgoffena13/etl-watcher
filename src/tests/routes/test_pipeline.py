import pytest
from httpx import AsyncClient

from src.tests.fixtures.pipeline import TEST_PIPELINE_POST_DATA


@pytest.mark.anyio
async def test_heartbeat(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_or_create_pipeline(async_client: AsyncClient):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201  # Created
    assert response.json() == {"id": 1}

    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 200
    assert response.json() == {"id": 1}
