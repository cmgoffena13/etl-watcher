import pytest
from httpx import AsyncClient

from src.database.address_lineage_utils import db_rebuild_closure_table_incremental
from src.tests.conftest import AsyncSessionLocal
from src.tests.fixtures.address import TEST_ADDRESS_POST_DATA
from src.tests.fixtures.pipeline import TEST_PIPELINE_POST_DATA


@pytest.mark.anyio
async def test_get_lineage_graph_endpoint(async_client: AsyncClient):
    """Test the lineage graph endpoint returns data."""

    # Create test data
    address1_response = await async_client.post("/address", json=TEST_ADDRESS_POST_DATA)
    assert address1_response.status_code == 201
    address1_id = address1_response.json()["id"]

    address2_data = TEST_ADDRESS_POST_DATA.copy()
    address2_data["name"] = "test_address_2"
    address2_response = await async_client.post("/address", json=address2_data)
    assert address2_response.status_code == 201
    address2_id = address2_response.json()["id"]

    # Create pipeline
    pipeline_response = await async_client.post(
        "/pipeline", json=TEST_PIPELINE_POST_DATA
    )
    assert pipeline_response.status_code == 201
    pipeline_id = pipeline_response.json()["id"]

    # Create address lineage
    lineage_data = {
        "pipeline_id": pipeline_id,
        "source_addresses": [TEST_ADDRESS_POST_DATA],
        "target_addresses": [address2_data],
    }
    lineage_response = await async_client.post("/address_lineage", json=lineage_data)
    assert lineage_response.status_code in [200, 201]

    # Manually rebuild the closure table since Celery tasks are mocked
    async with AsyncSessionLocal() as session:
        await db_rebuild_closure_table_incremental(
            session=session,
            connected_addresses={address1_id, address2_id},
            pipeline_id=pipeline_id,
        )

    # Refresh the materialized view to include the new lineage data
    await async_client.post("/lineage-graph/refresh")

    # Test lineage graph endpoint
    response = await async_client.get("/lineage-graph/")
    assert response.status_code == 200

    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)

    # Should have at least 2 nodes (the addresses we created)
    assert len(data["nodes"]) >= 2

    # Check node structure
    if data["nodes"]:
        node = data["nodes"][0]
        assert "id" in node
        assert "name" in node
        assert "address_type_name" in node
        assert "address_type_group_name" in node
