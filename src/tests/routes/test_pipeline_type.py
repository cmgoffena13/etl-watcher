import pytest
from httpx import AsyncClient

from src.tests.fixtures.pipeline_type import (
    TEST_PIPELINE_TYPE_PATCH_DATA,
    TEST_PIPELINE_TYPE_POST_DATA,
)


@pytest.mark.anyio
async def test_create_pipeline_type(async_client: AsyncClient):
    response = await async_client.post(
        "/pipeline_type", json=TEST_PIPELINE_TYPE_POST_DATA
    )
    assert response.status_code == 201
    assert response.json() == {"id": 1}


@pytest.mark.anyio
async def test_patch_pipeline_type(async_client: AsyncClient):
    response = await async_client.patch(
        "/pipeline_type", json=TEST_PIPELINE_TYPE_PATCH_DATA
    )
    assert response.status_code == 200
