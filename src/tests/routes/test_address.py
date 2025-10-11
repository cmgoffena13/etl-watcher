import pytest
from httpx import AsyncClient

from src.database.models.address import Address
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
async def test_get_address(async_client: AsyncClient):
    response = await async_client.post("/address", json=TEST_ADDRESS_POST_DATA)
    response = await async_client.get(f"/address/{response.json()['id']}")
    assert response.status_code == 200

    address_data = response.json()
    address = Address(**address_data)

    assert address.name == "test address"
    assert address.id == 1
    assert address.address_type_id == 1
    assert address.deprecated == False


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


@pytest.mark.anyio
async def test_address_hash_functionality(async_client: AsyncClient):
    """Test that address hash functionality works correctly for change detection."""

    # Create initial address using fixture
    response = await async_client.post("/address", json=TEST_ADDRESS_POST_DATA)
    assert response.status_code == 201
    address_id = response.json()["id"]

    # Test 1: Same data should not trigger update (hash unchanged)
    response = await async_client.post("/address", json=TEST_ADDRESS_POST_DATA)
    assert response.status_code == 200  # Should be 200 (no change)

    # Verify updated_at is still None (no change triggered)
    response = await async_client.get(f"/address/{address_id}")
    assert response.status_code == 200
    address_data = response.json()
    assert address_data["updated_at"] is None

    # Test 2: Different data should trigger update (hash changed)
    updated_data = {
        "name": "test address",
        "address_type_name": "database",  # Changed from "api"
        "address_type_group_name": "external",
        "primary_key": "id",  # Changed from None
    }

    response = await async_client.post("/address", json=updated_data)
    assert response.status_code == 200  # Should be 200 (updated)

    # Verify the database record was actually updated
    response = await async_client.get(f"/address/{address_id}")
    assert response.status_code == 200
    address_data = response.json()
    assert address_data["primary_key"] == "id"
    assert address_data["address_type_id"] == 2  # Should be updated to new type
    assert address_data["updated_at"] is not None  # Should be set after update
