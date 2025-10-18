import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.database.address_lineage_utils import db_rebuild_closure_table_incremental
from src.database.models.address_lineage import AddressLineageClosure
from src.tests.conftest import AsyncSessionLocal
from src.tests.fixtures.address_lineage import (
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

        # Verify the closure table was populated correctly

        # Check that we have the direct relationship (depth 1)
        direct_relationship = (
            await session.exec(
                select(AddressLineageClosure)
                .where(AddressLineageClosure.source_address_id == 1)
                .where(AddressLineageClosure.target_address_id == 2)
                .where(AddressLineageClosure.depth == 1)
            )
        ).first()

        assert direct_relationship is not None, (
            "Direct relationship should exist in closure table"
        )

        # Check that we have self-references (depth 0)
        source_self_ref = (
            await session.exec(
                select(AddressLineageClosure)
                .where(AddressLineageClosure.source_address_id == 1)
                .where(AddressLineageClosure.target_address_id == 1)
                .where(AddressLineageClosure.depth == 0)
            )
        ).first()

        target_self_ref = (
            await session.exec(
                select(AddressLineageClosure)
                .where(AddressLineageClosure.source_address_id == 2)
                .where(AddressLineageClosure.target_address_id == 2)
                .where(AddressLineageClosure.depth == 0)
            )
        ).first()

        assert source_self_ref is not None, "Source self-reference should exist"
        assert target_self_ref is not None, "Target self-reference should exist"

        # Verify total count of closure records
        all_closure_records = (
            await session.exec(select(AddressLineageClosure))
        ).fetchall()
        assert len(all_closure_records) == 3, (
            f"Expected 3 closure records (2 self-refs + 1 direct), got {len(all_closure_records)}"
        )
