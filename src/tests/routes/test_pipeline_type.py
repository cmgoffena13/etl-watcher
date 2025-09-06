import pytest
from httpx import AsyncClient

from src.tests.fixtures.pipeline_type import TEST_PIPELINE_TYPE_POST_DATA


@pytest.mark.anyio
async def test_create_pipeline_type(async_client: AsyncClient):
    response = await async_client.post(
        "/pipeline_type", json=TEST_PIPELINE_TYPE_POST_DATA
    )
    assert response.status_code == 201
    assert {"id": 1} == response.json()
