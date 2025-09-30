import pytest
from httpx import AsyncClient

from src.database.models.address_type import AddressType
from src.tests.fixtures.address_type import (
    TEST_ADDRESS_TYPE_PATCH_DATA,
    TEST_ADDRESS_TYPE_PATCH_OUTPUT_DATA,
    TEST_ADDRESS_TYPE_POST_DATA,
)


@pytest.mark.anyio
async def test_get_or_create_address_type(async_client: AsyncClient):
    response = await async_client.post(
        "/address_type", json=TEST_ADDRESS_TYPE_POST_DATA
    )
    assert response.status_code == 201  # Created
    assert response.json() == {"id": 1}

    response = await async_client.post(
        "/address_type", json=TEST_ADDRESS_TYPE_POST_DATA
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1}


@pytest.mark.anyio
async def test_get_address_type(async_client: AsyncClient):
    response = await async_client.post(
        "/address_type", json=TEST_ADDRESS_TYPE_POST_DATA
    )
    response = await async_client.get(f"/address_type/{response.json()['id']}")
    assert response.status_code == 200

    address_type_data = response.json()
    address_type = AddressType(**address_type_data)

    assert address_type.name == "iam"
    assert address_type.group_name == "database"
    assert address_type.id == 1


@pytest.mark.anyio
async def test_patch_address_type(async_client: AsyncClient):
    # First create the address_type to then be able to patch
    await async_client.post("/address_type", json=TEST_ADDRESS_TYPE_POST_DATA)
    response = await async_client.patch(
        "/address_type", json=TEST_ADDRESS_TYPE_PATCH_DATA
    )
    data = response.json()
    assert response.status_code == 200
    for k, v in TEST_ADDRESS_TYPE_PATCH_OUTPUT_DATA.items():
        assert data[k] == v
    assert "created_at" in data
    assert "updated_at" in data
