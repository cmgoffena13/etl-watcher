import pytest
from httpx import AsyncClient

from src.database.models.pipeline import Pipeline
from src.tests.fixtures.pipeline import (
    TEST_PIPELINE_PATCH_DATA,
    TEST_PIPELINE_PATCH_OUTPUT_DATA,
    TEST_PIPELINE_POST_DATA,
)
from src.tests.fixtures.pipeline_execution import (
    TEST_PIPELINE_EXECUTION_END_DATA,
    TEST_PIPELINE_EXECUTION_START_DATA,
)


@pytest.mark.anyio
async def test_heartbeat(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_or_create_pipeline(async_client: AsyncClient):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201  # Created
    assert response.json() == {
        "id": 1,
        "active": True,
        "load_lineage": True,
        "watermark": None,
    }

    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "active": True,
        "load_lineage": True,
        "watermark": None,
    }


@pytest.mark.anyio
async def test_get_pipeline(async_client: AsyncClient):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "active": True,
        "load_lineage": True,
        "watermark": None,
    }
    response = await async_client.get(f"/pipeline/{response.json()['id']}")
    assert response.status_code == 200

    pipeline_data = response.json()
    pipeline = Pipeline(**pipeline_data)

    assert pipeline.name == "test pipeline 1"
    assert pipeline.pipeline_type_id == 1
    assert pipeline.next_watermark == "10"
    assert pipeline.id == 1


@pytest.mark.anyio
async def test_pipeline_hash_functionality(async_client: AsyncClient):
    """Test that pipeline hash functionality works correctly for change detection."""

    # Create initial pipeline using fixture
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    # Test 1: Same data should not trigger update (hash unchanged)
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 200  # Should be 200 (no change)

    # Verify updated_at is still None (no change triggered)
    response = await async_client.get(f"/pipeline/{pipeline_id}")
    assert response.status_code == 200
    pipeline_data = response.json()
    assert pipeline_data["updated_at"] is None

    # Test 2: Different data should trigger update (hash changed)
    updated_data = {
        "name": "Test Pipeline 1",
        "pipeline_type_name": "transformation",  # Changed from "extraction"
        "pipeline_type_group_name": "databricks",
        "freshness_number": 15,  # Changed from None
        "freshness_datepart": "minute",
        "timeliness_number": 30,  # Changed from None
        "timeliness_datepart": "minute",
    }

    response = await async_client.post("/pipeline", json=updated_data)
    assert response.status_code == 200  # Should be 200 (updated)

    # Verify the database record was actually updated
    response = await async_client.get(f"/pipeline/{pipeline_id}")
    assert response.status_code == 200
    pipeline_data = response.json()
    assert pipeline_data["freshness_number"] == 15
    assert pipeline_data["timeliness_number"] == 30
    assert pipeline_data["freshness_datepart"] == "minute"
    assert pipeline_data["timeliness_datepart"] == "minute"
    assert pipeline_data["pipeline_type_id"] == 2  # Should be updated to new type
    assert pipeline_data["updated_at"] is not None  # Should be set after update

    # Test 3: Update with watermark should work
    # First, set a watermark value via PATCH
    patch_data = {"id": pipeline_id, "watermark": "2024-01-01T10:00:00Z"}
    response = await async_client.patch("/pipeline", json=patch_data)
    assert response.status_code == 200

    # Now test POST with next_watermark - should return watermark value too
    watermark_data = {
        "name": "Test Pipeline 1",
        "pipeline_type_name": "extraction",
        "pipeline_type_group_name": "databricks",
        "freshness_number": 60,  # Changed again
        "freshness_datepart": "minute",  # Required with freshness_number
        "timeliness_number": 120,  # Changed again
        "timeliness_datepart": "minute",  # Required with timeliness_number
        "next_watermark": "2024-01-01T12:00:00Z",  # Add next_watermark
    }

    response = await async_client.post("/pipeline", json=watermark_data)
    assert response.status_code == 200
    assert response.json()["watermark"] is not None

    # Verify the database record was updated again
    response = await async_client.get(f"/pipeline/{pipeline_id}")
    assert response.status_code == 200
    pipeline_data = response.json()
    assert pipeline_data["freshness_number"] == 60
    assert pipeline_data["timeliness_number"] == 120


@pytest.mark.anyio
async def test_patch_pipeline(async_client: AsyncClient):
    # First create the pipeline to then be able to patch
    await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    response = await async_client.patch("/pipeline", json=TEST_PIPELINE_PATCH_DATA)
    data = response.json()
    assert response.status_code == 200
    for k, v in TEST_PIPELINE_PATCH_OUTPUT_DATA.items():
        assert data[k] == v
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_watermark_increment_pipeline(async_client: AsyncClient):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.json() == {
        "id": 1,
        "active": True,
        "load_lineage": True,
        "watermark": None,
    }

    response = await async_client.post(
        "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
    )
    assert response.status_code == 201

    response = await async_client.get("/pipeline")
    data = response.json()[0]

    assert data.get("watermark") == None
    assert data.get("next_watermark") == str(10)

    response = await async_client.post(
        "/end_pipeline_execution", json=TEST_PIPELINE_EXECUTION_END_DATA
    )
    assert response.status_code == 204

    response = await async_client.get("/pipeline")
    data = response.json()[0]
    assert data.get("watermark") == str(10)
    assert data.get("next_watermark") == str(10)

    TEST_PIPELINE_POST_DATA["next_watermark"] = str(12)
    new_data = TEST_PIPELINE_POST_DATA
    response = await async_client.post("/pipeline", json=new_data)
    assert response.json() == {
        "id": 1,
        "active": True,
        "load_lineage": False,
        "watermark": "10",
    }

    response = await async_client.post(
        "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
    )
    assert response.status_code == 201

    response = await async_client.get("/pipeline")
    data = response.json()[0]
    assert data.get("watermark") == str(10)
    assert data.get("next_watermark") == str(12)

    response = await async_client.post(
        "/end_pipeline_execution", json=TEST_PIPELINE_EXECUTION_END_DATA
    )
    assert response.status_code == 204

    response = await async_client.get("/pipeline")
    data = response.json()[0]

    assert data.get("watermark") == str(12)
    assert data.get("next_watermark") == str(12)


@pytest.mark.anyio
async def test_pipeline_validation_freshness_timeliness_fields(
    async_client: AsyncClient,
):
    """Test that freshness and timeliness fields must be provided together."""

    # Test 1: Only freshness_number provided (should fail)
    response = await async_client.post(
        "/pipeline",
        json={
            "name": "test pipeline validation",
            "pipeline_type_name": "extraction",
            "freshness_number": 5,
        },
    )
    assert response.status_code == 422
    assert (
        "freshness_number and freshness_datepart must be provided together"
        in response.json()["detail"][0]["msg"]
    )

    # Test 2: Only freshness_datepart provided (should fail)
    response = await async_client.post(
        "/pipeline",
        json={
            "name": "test pipeline validation",
            "pipeline_type_name": "extraction",
            "freshness_datepart": "hour",
        },
    )
    assert response.status_code == 422
    assert (
        "freshness_number and freshness_datepart must be provided together"
        in response.json()["detail"][0]["msg"]
    )

    # Test 3: Only timeliness_number provided (should fail)
    response = await async_client.post(
        "/pipeline",
        json={
            "name": "test pipeline validation",
            "pipeline_type_name": "extraction",
            "timeliness_number": 10,
        },
    )
    assert response.status_code == 422
    assert (
        "timeliness_number and timeliness_datepart must be provided together"
        in response.json()["detail"][0]["msg"]
    )

    # Test 4: Only timeliness_datepart provided (should fail)
    response = await async_client.post(
        "/pipeline",
        json={
            "name": "test pipeline validation",
            "pipeline_type_name": "extraction",
            "timeliness_datepart": "minute",
        },
    )
    assert response.status_code == 422
    assert (
        "timeliness_number and timeliness_datepart must be provided together"
        in response.json()["detail"][0]["msg"]
    )

    # Test 5: Both freshness fields provided (should succeed)
    response = await async_client.post(
        "/pipeline",
        json={
            "name": "test pipeline validation success",
            "pipeline_type_name": "extraction",
            "freshness_number": 5,
            "freshness_datepart": "hour",
        },
    )
    assert response.status_code == 201

    # Test 6: Both timeliness fields provided (should succeed)
    response = await async_client.post(
        "/pipeline",
        json={
            "name": "test pipeline validation success 2",
            "pipeline_type_name": "extraction",
            "timeliness_number": 10,
            "timeliness_datepart": "minute",
        },
    )
    assert response.status_code == 201

    # Test 7: Neither field provided (should succeed)
    response = await async_client.post(
        "/pipeline",
        json={
            "name": "test pipeline validation success 3",
            "pipeline_type_name": "extraction",
        },
    )
    assert response.status_code == 201
