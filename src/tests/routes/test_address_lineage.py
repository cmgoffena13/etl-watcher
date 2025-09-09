import pytest
from httpx import AsyncClient

from src.tests.fixtures.address_lineage import (
    TEST_ADDRESS_LINEAGE_GET_OUTPUT_DATA,
    TEST_ADDRESS_LINEAGE_MULTIPLE_SOURCES_AND_TARGETS_DATA,
    TEST_ADDRESS_LINEAGE_MULTIPLE_SOURCES_DATA,
    TEST_ADDRESS_LINEAGE_MULTIPLE_TARGETS_DATA,
    TEST_ADDRESS_LINEAGE_POST_DATA,
    TEST_ADDRESS_LINEAGE_POST_OUTPUT_DATA,
    TEST_ADDRESS_LINEAGE_UPDATE_DATA,
)
from src.tests.fixtures.pipeline import TEST_PIPELINE_POST_DATA


@pytest.mark.anyio
async def test_create_address_lineage(async_client: AsyncClient):
    """Test creating address lineage relationships for a pipeline"""
    # First create a pipeline with load_lineage = True
    pipeline_data = TEST_PIPELINE_POST_DATA.copy()
    pipeline_data["load_lineage"] = True

    pipeline_response = await async_client.post("/pipeline", json=pipeline_data)
    assert pipeline_response.status_code == 201
    pipeline_result = pipeline_response.json()
    assert pipeline_result["load_lineage"] == True

    response = await async_client.post(
        "/address_lineage", json=TEST_ADDRESS_LINEAGE_POST_DATA
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data == TEST_ADDRESS_LINEAGE_POST_OUTPUT_DATA


@pytest.mark.anyio
async def test_get_address_lineage_by_pipeline(async_client: AsyncClient):
    """Test getting address lineage relationships for a pipeline"""
    # First create a pipeline with load_lineage = True
    pipeline_data = TEST_PIPELINE_POST_DATA.copy()
    pipeline_data["load_lineage"] = True

    pipeline_response = await async_client.post("/pipeline", json=pipeline_data)
    assert pipeline_response.status_code == 201

    # Create address lineage relationships
    await async_client.post("/address_lineage", json=TEST_ADDRESS_LINEAGE_POST_DATA)

    # Now get the lineage relationships
    response = await async_client.get("/address_lineage/1")
    assert response.status_code == 200
    response_data = response.json()

    # The API returns a list of AddressLineage objects directly
    assert response_data == TEST_ADDRESS_LINEAGE_GET_OUTPUT_DATA


@pytest.mark.anyio
async def test_create_address_lineage_multiple_sources(async_client: AsyncClient):
    """Test creating lineage with multiple source addresses"""
    # First create a pipeline
    pipeline_data = TEST_PIPELINE_POST_DATA.copy()
    pipeline_data["load_lineage"] = True

    await async_client.post("/pipeline", json=pipeline_data)

    # Create lineage with multiple source addresses
    response = await async_client.post(
        "/address_lineage", json=TEST_ADDRESS_LINEAGE_MULTIPLE_SOURCES_DATA
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["lineage_relationships_created"] == 2  # 2 sources × 1 target


@pytest.mark.anyio
async def test_create_address_lineage_multiple_targets(async_client: AsyncClient):
    """Test creating lineage with multiple target addresses"""
    # First create a pipeline
    pipeline_data = TEST_PIPELINE_POST_DATA.copy()
    pipeline_data["load_lineage"] = True

    await async_client.post("/pipeline", json=pipeline_data)

    # Create lineage with multiple target addresses
    response = await async_client.post(
        "/address_lineage", json=TEST_ADDRESS_LINEAGE_MULTIPLE_TARGETS_DATA
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["lineage_relationships_created"] == 2  # 1 source × 2 targets


@pytest.mark.anyio
async def test_create_address_lineage_multiple_sources_and_targets(
    async_client: AsyncClient,
):
    """Test creating lineage with multiple source and target addresses"""
    # First create a pipeline
    pipeline_data = TEST_PIPELINE_POST_DATA.copy()
    pipeline_data["load_lineage"] = True

    await async_client.post("/pipeline", json=pipeline_data)

    # Create lineage with multiple sources and targets
    response = await async_client.post(
        "/address_lineage", json=TEST_ADDRESS_LINEAGE_MULTIPLE_SOURCES_AND_TARGETS_DATA
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["lineage_relationships_created"] == 4  # 2 sources × 2 targets


@pytest.mark.anyio
async def test_update_address_lineage_replaces_existing(async_client: AsyncClient):
    """Test that updating lineage replaces existing relationships"""
    # First create a pipeline
    pipeline_data = TEST_PIPELINE_POST_DATA.copy()
    pipeline_data["load_lineage"] = True

    await async_client.post("/pipeline", json=pipeline_data)

    # Create initial lineage
    response = await async_client.post(
        "/address_lineage", json=TEST_ADDRESS_LINEAGE_POST_DATA
    )
    assert response.status_code == 201
    assert response.json()["lineage_relationships_created"] == 1

    # Update with different addresses
    response = await async_client.post(
        "/address_lineage", json=TEST_ADDRESS_LINEAGE_UPDATE_DATA
    )
    assert response.status_code == 201
    assert response.json()["lineage_relationships_created"] == 1

    # Verify only the new relationship exists
    get_response = await async_client.get("/address_lineage/1")
    assert get_response.status_code == 200
    response_data = get_response.json()

    # The API returns a list of AddressLineage objects directly
    assert isinstance(response_data, list)
    assert len(response_data) == 1
