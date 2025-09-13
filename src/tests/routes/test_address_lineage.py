import pytest
from httpx import AsyncClient

from src.database.address_lineage_utils import db_rebuild_closure_table_incremental
from src.tests.conftest import AsyncSessionLocal
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
async def test_get_address_lineage_by_address(async_client: AsyncClient):
    """Test getting address lineage relationships for an address"""
    # First create a pipeline with load_lineage = True
    pipeline_data = TEST_PIPELINE_POST_DATA.copy()
    pipeline_data["load_lineage"] = True

    pipeline_response = await async_client.post("/pipeline", json=pipeline_data)
    assert pipeline_response.status_code == 201

    # Create address lineage relationships
    await async_client.post("/address_lineage", json=TEST_ADDRESS_LINEAGE_POST_DATA)

    # Manually trigger closure table rebuild since background tasks are mocked
    async with AsyncSessionLocal() as session:
        await db_rebuild_closure_table_incremental(
            session=session,
            connected_addresses={1, 2},  # source and target address IDs
            pipeline_id=1,
        )

    # Now get the lineage relationships for the source address (id=1)
    response = await async_client.get("/address_lineage/1")
    assert response.status_code == 200
    response_data = response.json()

    # The API returns a list of AddressLineageClosureOutput objects
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


@pytest.mark.anyio
async def test_closure_table_rebuild_function(async_client: AsyncClient):
    """Test the closure table rebuild function directly"""

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

    # Test the closure table rebuild function directly
    async with AsyncSessionLocal() as session:
        await db_rebuild_closure_table_incremental(
            session=session,
            connected_addresses={1, 2},  # The addresses created by the test
            pipeline_id=1,
        )

    # Now test that the get endpoint works
    get_response = await async_client.get("/address_lineage/1")
    assert get_response.status_code == 200
    response_data = get_response.json()

    # Should have the relationship in the closure table
    assert isinstance(response_data, list)
    assert len(response_data) == 1
    assert response_data[0]["source_address_id"] == 1
    assert response_data[0]["target_address_id"] == 2
