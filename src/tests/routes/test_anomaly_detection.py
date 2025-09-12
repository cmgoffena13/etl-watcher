import pytest
from httpx import AsyncClient

from src.tests.fixtures.anomaly_detection import (
    TEST_ANOMALY_DETECTION_RULE_PATCH_DATA,
    TEST_ANOMALY_DETECTION_RULE_PATCH_OUTPUT_DATA,
    TEST_ANOMALY_DETECTION_RULE_POST_DATA,
)
from src.tests.fixtures.pipeline import TEST_PIPELINE_POST_DATA


@pytest.mark.anyio
async def test_get_or_create_anomaly_detection_rule(async_client: AsyncClient):
    # Create a pipeline to then be able to create an anomaly detection rule
    await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    response = await async_client.post(
        "/anomaly_detection_rule", json=TEST_ANOMALY_DETECTION_RULE_POST_DATA
    )
    assert response.status_code == 201  # Created
    assert response.json() == {"id": 1}

    response = await async_client.post(
        "/anomaly_detection_rule", json=TEST_ANOMALY_DETECTION_RULE_POST_DATA
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1}


@pytest.mark.anyio
async def test_patch_anomaly_detection_rule(async_client: AsyncClient):
    # Create a pipeline to then be able to create an anomaly detection rule
    await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    # First create the address_type to then be able to patch
    await async_client.post(
        "/anomaly_detection_rule", json=TEST_ANOMALY_DETECTION_RULE_POST_DATA
    )
    response = await async_client.patch(
        "/anomaly_detection_rule", json=TEST_ANOMALY_DETECTION_RULE_PATCH_DATA
    )
    data = response.json()
    assert response.status_code == 200
    for k, v in TEST_ANOMALY_DETECTION_RULE_PATCH_OUTPUT_DATA.items():
        assert data[k] == v
    assert "created_at" in data
    assert "updated_at" in data
