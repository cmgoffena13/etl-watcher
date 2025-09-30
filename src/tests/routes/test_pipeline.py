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
