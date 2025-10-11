import pytest
from httpx import AsyncClient

from src.database.models.pipeline_type import PipelineType
from src.tests.fixtures.pipeline_type import (
    TEST_PIPELINE_TYPE_PATCH_DATA,
    TEST_PIPELINE_TYPE_PATCH_OUTPUT_DATA,
    TEST_PIPELINE_TYPE_POST_DATA,
)


@pytest.mark.anyio
async def test_get_or_create_pipeline_type(async_client: AsyncClient):
    response = await async_client.post(
        "/pipeline_type", json=TEST_PIPELINE_TYPE_POST_DATA
    )
    assert response.status_code == 201  # Created
    assert response.json() == {"id": 1}  # Pipeline tests already create pipeline type

    response = await async_client.post(
        "/pipeline_type", json=TEST_PIPELINE_TYPE_POST_DATA
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1}


@pytest.mark.anyio
async def test_get_pipeline_type(async_client: AsyncClient):
    response = await async_client.post(
        "/pipeline_type", json=TEST_PIPELINE_TYPE_POST_DATA
    )
    response = await async_client.get(f"/pipeline_type/{response.json()['id']}")
    assert response.status_code == 200

    pipeline_type_data = response.json()
    pipeline_type = PipelineType(**pipeline_type_data)

    assert pipeline_type.name == "audit"
    assert pipeline_type.freshness_number == 10
    assert pipeline_type.freshness_datepart == "hour"
    assert pipeline_type.mute_freshness_check == False
    assert pipeline_type.id == 1


@pytest.mark.anyio
async def test_patch_pipeline_type(async_client: AsyncClient):
    # First create the pipeline_type to then be able to patch
    await async_client.post("/pipeline_type", json=TEST_PIPELINE_TYPE_POST_DATA)

    # Test ID-based update
    response = await async_client.patch(
        "/pipeline_type", json=TEST_PIPELINE_TYPE_PATCH_DATA
    )
    data = response.json()
    assert response.status_code == 200
    for k, v in TEST_PIPELINE_TYPE_PATCH_OUTPUT_DATA.items():
        assert data[k] == v
    assert "created_at" in data
    assert "updated_at" in data

    # Test name-based update
    patch_data = {
        "name": "audit_patched",  # Use the current name after the first patch
        "freshness_number": 30,
        "freshness_datepart": "minute",
    }
    response = await async_client.patch("/pipeline_type", json=patch_data)
    data = response.json()
    assert response.status_code == 200
    assert data["freshness_number"] == 30
    assert data["freshness_datepart"] == "minute"
    assert "updated_at" in data

    # Test validation error when neither ID nor name is provided
    patch_data = {"freshness_number": 30}
    response = await async_client.patch("/pipeline_type", json=patch_data)
    assert response.status_code == 422
    assert (
        "Either 'id' or 'name' must be provided" in response.json()["detail"][0]["msg"]
    )
