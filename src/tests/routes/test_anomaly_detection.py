import pendulum
import pytest
from httpx import AsyncClient

from src.database.anomaly_detection_utils import db_detect_anomalies_for_pipeline
from src.tests.conftest import AsyncSessionLocal
from src.tests.fixtures.anomaly_detection import (
    TEST_ANOMALY_DETECTION_RULE_PATCH_DATA,
    TEST_ANOMALY_DETECTION_RULE_PATCH_OUTPUT_DATA,
    TEST_ANOMALY_DETECTION_RULE_POST_DATA,
)
from src.tests.fixtures.pipeline import TEST_PIPELINE_POST_DATA
from src.tests.fixtures.pipeline_execution import (
    TEST_PIPELINE_EXECUTION_END_DATA,
    TEST_PIPELINE_EXECUTION_START_DATA,
)


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


@pytest.mark.anyio
async def test_anomaly_detection_result_skip(
    async_client: AsyncClient, mock_slack_notifications
):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule", json=TEST_ANOMALY_DETECTION_RULE_POST_DATA
    )
    assert response.status_code == 201

    response = await async_client.post(
        "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
    )
    execution_id = response.json()["id"]
    response = await async_client.post(
        "/end_pipeline_execution", json=TEST_PIPELINE_EXECUTION_END_DATA
    )
    assert response.status_code == 204

    # Call anomaly detection directly since background tasks don't run in tests
    async with AsyncSessionLocal() as session:
        await db_detect_anomalies_for_pipeline(session, pipeline_id, execution_id)

    mock_slack_notifications.assert_not_called()


@pytest.mark.anyio
async def test_anomaly_detection_result_success(async_client: AsyncClient):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule", json=TEST_ANOMALY_DETECTION_RULE_POST_DATA
    )
    assert response.status_code == 201

    for i in range(1, 6):  # Minimum executions 5
        post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
        response = await async_client.post(
            "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
        )
        execution_id = response.json()["id"]
        post_data.update(
            {
                "id": response.json()["id"],
            }
        )
        response = await async_client.post(
            "/end_pipeline_execution", json=TEST_PIPELINE_EXECUTION_END_DATA
        )
        assert response.status_code == 204
        # Call anomaly detection directly since background tasks don't run in tests
        async with AsyncSessionLocal() as session:
            await db_detect_anomalies_for_pipeline(session, pipeline_id, execution_id)


@pytest.mark.anyio
async def test_anomaly_detection_result_failure(
    async_client: AsyncClient, mock_slack_notifications
):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule", json=TEST_ANOMALY_DETECTION_RULE_POST_DATA
    )
    assert response.status_code == 201

    for i in range(1, 6):
        response = await async_client.post(
            "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
        )
        execution_id = response.json()["id"]

        if (
            i == 5
        ):  # Trigger anomaly by giving ridiculous end_date to create high duration_seconds
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()

            ridiculous_end_date = pendulum.now("UTC").add(seconds=999999)
            post_data.update(
                {
                    "end_date": ridiculous_end_date.isoformat(),
                }
            )
        else:
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()

        post_data.update(
            {
                "id": response.json()["id"],
            }
        )
        response = await async_client.post("/end_pipeline_execution", json=post_data)
        assert response.status_code == 204
        # Call anomaly detection directly since background tasks don't run in tests (mocked)
        async with AsyncSessionLocal() as session:
            await db_detect_anomalies_for_pipeline(session, pipeline_id, execution_id)

    mock_slack_notifications.assert_called_once()
    call_args = mock_slack_notifications.call_args
    assert "Anomaly detected in pipeline" in call_args[1]["message"]
    assert "execution(s) flagged" in call_args[1]["message"]
    assert "Metric" in call_args[1]["details"]
    assert "Threshold Multiplier" in call_args[1]["details"]
    assert "Lookback Days" in call_args[1]["details"]
    assert "Anomalies" in call_args[1]["details"]
