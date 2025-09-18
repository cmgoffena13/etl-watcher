import pytest
from httpx import AsyncClient

from src.tests.fixtures.address import (
    TEST_ADDRESS_DATABASE_GET_OUTPUT_DATA,
    TEST_ADDRESS_DATABASE_POST_DATA,
    TEST_ADDRESS_PATCH_DATA,
    TEST_ADDRESS_PATCH_OUTPUT_DATA,
    TEST_ADDRESS_POST_DATA,
)


@pytest.mark.anyio
async def test_get_or_create_address(async_client: AsyncClient):
    response = await async_client.post("/address", json=TEST_ADDRESS_POST_DATA)
    assert response.status_code == 201  # Created
    assert response.json() == {"id": 1}

    response = await async_client.post("/address", json=TEST_ADDRESS_POST_DATA)
    assert response.status_code == 200
    assert response.json() == {"id": 1}


@pytest.mark.anyio
async def test_patch_address(async_client: AsyncClient):
    # First create the pipeline to then be able to patch
    await async_client.post("/address", json=TEST_ADDRESS_POST_DATA)
    response = await async_client.patch("/address", json=TEST_ADDRESS_PATCH_DATA)
    data = response.json()
    assert response.status_code == 200
    for k, v in TEST_ADDRESS_PATCH_OUTPUT_DATA.items():
        assert data[k] == v
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_database_address(async_client: AsyncClient):
    response = await async_client.post("/address", json=TEST_ADDRESS_DATABASE_POST_DATA)
    assert response.status_code == 201
    assert response.json() == {"id": 1}

    response = await async_client.get("/address")
    assert response.status_code == 200
    data = response.json()[0]
    for k, v in TEST_ADDRESS_DATABASE_GET_OUTPUT_DATA.items():
        assert data[k] == v
