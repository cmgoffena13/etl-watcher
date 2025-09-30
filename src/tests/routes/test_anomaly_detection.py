import pendulum
import pytest
from httpx import AsyncClient

from src.database.anomaly_detection_utils import (
    db_detect_anomalies_for_pipeline_execution,
)
from src.database.models.anomaly_detection import AnomalyDetectionRule
from src.tests.conftest import AsyncSessionLocal
from src.tests.fixtures.anomaly_detection import (
    TEST_ANOMALY_DETECTION_RULE_DURATION_SECONDS_POST_DATA,
    TEST_ANOMALY_DETECTION_RULE_INSERTS_POST_DATA,
    TEST_ANOMALY_DETECTION_RULE_PATCH_DATA,
    TEST_ANOMALY_DETECTION_RULE_PATCH_OUTPUT_DATA,
    TEST_ANOMALY_DETECTION_RULE_SOFT_DELETES_POST_DATA,
    TEST_ANOMALY_DETECTION_RULE_THROUGHPUT_POST_DATA,
    TEST_ANOMALY_DETECTION_RULE_TOTAL_ROWS_POST_DATA,
    TEST_ANOMALY_DETECTION_RULE_UPDATES_POST_DATA,
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
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_DURATION_SECONDS_POST_DATA,
    )
    assert response.status_code == 201  # Created
    assert response.json() == {"id": 1}

    response = await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_DURATION_SECONDS_POST_DATA,
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1}


@pytest.mark.anyio
async def test_get_anomaly_detection_rule(async_client: AsyncClient):
    await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    response = await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_DURATION_SECONDS_POST_DATA,
    )
    response = await async_client.get(
        f"/anomaly_detection_rule/{response.json()['id']}"
    )
    assert response.status_code == 200

    rule_data = response.json()
    rule = AnomalyDetectionRule(**rule_data)

    assert rule.pipeline_id == 1
    assert rule.metric_field == "duration_seconds"
    assert (
        float(rule.z_threshold) == 1.0
    )  # Decimal comes back as string to promote accuracy
    assert rule.lookback_days == 10
    assert rule.minimum_executions == 5
    assert rule.active == True
    assert rule.id == 1


@pytest.mark.anyio
async def test_patch_anomaly_detection_rule(async_client: AsyncClient):
    # Create a pipeline to then be able to create an anomaly detection rule
    await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    # First create the address_type to then be able to patch
    await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_DURATION_SECONDS_POST_DATA,
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
    async_client: AsyncClient, mock_anomaly_alert
):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_DURATION_SECONDS_POST_DATA,
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
        await db_detect_anomalies_for_pipeline_execution(
            session, pipeline_id, execution_id
        )

    mock_anomaly_alert.assert_not_called()


@pytest.mark.anyio
async def test_anomaly_detection_result_success(async_client: AsyncClient):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_DURATION_SECONDS_POST_DATA,
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
            await db_detect_anomalies_for_pipeline_execution(
                session, pipeline_id, execution_id
            )


@pytest.mark.anyio
async def test_anomaly_detection_duration_seconds_result_failure(
    async_client: AsyncClient, mock_anomaly_alert
):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_DURATION_SECONDS_POST_DATA,
    )
    assert response.status_code == 201

    for i in range(1, 7):
        response = await async_client.post(
            "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
        )
        execution_id = response.json()["id"]

        if (
            i == 6
        ):  # Trigger anomaly by giving ridiculous end_date to create high duration_seconds
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()

            ridiculous_end_date = pendulum.now("UTC").add(seconds=999999)
            post_data.update(
                {
                    "end_date": ridiculous_end_date.isoformat(),
                }
            )
        else:
            # Vary the baseline data to create different duration_seconds values
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            # Vary end_date to create different duration_seconds
            post_data.update(
                {
                    "end_date": pendulum.now("UTC")
                    .add(minutes=30 + (i * 10))
                    .isoformat(),  # 40, 50, 60, 70, 80 minutes
                }
            )

        post_data.update(
            {
                "id": response.json()["id"],
            }
        )
        response = await async_client.post("/end_pipeline_execution", json=post_data)
        assert response.status_code == 204
        # Call anomaly detection directly since background tasks don't run in tests (mocked)
        async with AsyncSessionLocal() as session:
            await db_detect_anomalies_for_pipeline_execution(
                session, pipeline_id, execution_id
            )

    mock_anomaly_alert.assert_called_once()
    call_args = mock_anomaly_alert.call_args
    assert "Anomalies detected in Pipeline" in call_args[1]["message"]
    assert "flagged" in call_args[1]["message"]
    assert "Total Anomalies" in call_args[1]["details"]
    assert "Metrics" in call_args[1]["details"]
    assert "Anomalies" in call_args[1]["details"]


@pytest.mark.anyio
async def test_anomaly_detection_inserts_result_failure(
    async_client: AsyncClient, mock_anomaly_alert
):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_INSERTS_POST_DATA,
    )
    assert response.status_code == 201

    for i in range(1, 7):
        response = await async_client.post(
            "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
        )
        execution_id = response.json()["id"]

        if i == 6:  # Trigger anomaly by giving ridiculous inserts count
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            post_data.update(
                {
                    "inserts": 999999,
                }
            )
        else:
            # Vary the baseline data to create different inserts values
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            post_data.update(
                {
                    "inserts": 8 + (i * 2),  # 10, 12, 14, 16, 18
                }
            )

        post_data.update(
            {
                "id": response.json()["id"],
            }
        )
        response = await async_client.post("/end_pipeline_execution", json=post_data)
        assert response.status_code == 204
        # Call anomaly detection directly since background tasks don't run in tests (mocked)
        async with AsyncSessionLocal() as session:
            await db_detect_anomalies_for_pipeline_execution(
                session, pipeline_id, execution_id
            )

    mock_anomaly_alert.assert_called_once()
    call_args = mock_anomaly_alert.call_args
    assert "Anomalies detected in Pipeline" in call_args[1]["message"]
    assert "flagged" in call_args[1]["message"]
    assert "Total Anomalies" in call_args[1]["details"]
    assert "Metrics" in call_args[1]["details"]
    assert "Anomalies" in call_args[1]["details"]


@pytest.mark.anyio
async def test_anomaly_detection_updates_result_failure(
    async_client: AsyncClient, mock_anomaly_alert
):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_UPDATES_POST_DATA,
    )
    assert response.status_code == 201

    for i in range(1, 7):
        response = await async_client.post(
            "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
        )
        execution_id = response.json()["id"]

        if i == 6:  # Trigger anomaly by giving ridiculous updates count
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            post_data.update(
                {
                    "updates": 999999,
                }
            )
        else:
            # Vary the baseline data to create different updates values
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            post_data.update(
                {
                    "updates": 10 + (i * 2),  # 12, 14, 16, 18, 20
                }
            )

        post_data.update(
            {
                "id": response.json()["id"],
            }
        )
        response = await async_client.post("/end_pipeline_execution", json=post_data)
        assert response.status_code == 204
        # Call anomaly detection directly since background tasks don't run in tests (mocked)
        async with AsyncSessionLocal() as session:
            await db_detect_anomalies_for_pipeline_execution(
                session, pipeline_id, execution_id
            )

    mock_anomaly_alert.assert_called_once()
    call_args = mock_anomaly_alert.call_args
    assert "Anomalies detected in Pipeline" in call_args[1]["message"]
    assert "flagged" in call_args[1]["message"]
    assert "Total Anomalies" in call_args[1]["details"]
    assert "Metrics" in call_args[1]["details"]
    assert "Anomalies" in call_args[1]["details"]


@pytest.mark.anyio
async def test_anomaly_detection_soft_deletes_result_failure(
    async_client: AsyncClient, mock_anomaly_alert
):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_SOFT_DELETES_POST_DATA,
    )
    assert response.status_code == 201

    for i in range(1, 7):
        response = await async_client.post(
            "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
        )
        execution_id = response.json()["id"]

        if i == 6:  # Trigger anomaly by giving ridiculous soft_deletes count
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            post_data.update(
                {
                    "soft_deletes": 999999,
                }
            )
        else:
            # Vary the baseline data to create different soft_deletes values
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            post_data.update(
                {
                    "soft_deletes": 12 + (i * 2),  # 14, 16, 18, 20, 22
                }
            )

        post_data.update(
            {
                "id": response.json()["id"],
            }
        )
        response = await async_client.post("/end_pipeline_execution", json=post_data)
        assert response.status_code == 204
        # Call anomaly detection directly since background tasks don't run in tests (mocked)
        async with AsyncSessionLocal() as session:
            await db_detect_anomalies_for_pipeline_execution(
                session, pipeline_id, execution_id
            )

    mock_anomaly_alert.assert_called_once()
    call_args = mock_anomaly_alert.call_args
    assert "Anomalies detected in Pipeline" in call_args[1]["message"]
    assert "flagged" in call_args[1]["message"]
    assert "Total Anomalies" in call_args[1]["details"]
    assert "Metrics" in call_args[1]["details"]
    assert "Anomalies" in call_args[1]["details"]


@pytest.mark.anyio
async def test_anomaly_detection_total_rows_result_failure(
    async_client: AsyncClient, mock_anomaly_alert
):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_TOTAL_ROWS_POST_DATA,
    )
    assert response.status_code == 201

    for i in range(1, 7):
        response = await async_client.post(
            "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
        )
        execution_id = response.json()["id"]

        if i == 6:  # Trigger anomaly by giving ridiculous total_rows count
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            post_data.update(
                {
                    "total_rows": 999999,
                }
            )
        else:
            # Vary the baseline data to create different total_rows values
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            post_data.update(
                {
                    "total_rows": 30 + (i * 5),  # 35, 40, 45, 50, 55
                }
            )

        post_data.update(
            {
                "id": response.json()["id"],
            }
        )
        response = await async_client.post("/end_pipeline_execution", json=post_data)
        assert response.status_code == 204
        # Call anomaly detection directly since background tasks don't run in tests (mocked)
        async with AsyncSessionLocal() as session:
            await db_detect_anomalies_for_pipeline_execution(
                session, pipeline_id, execution_id
            )

    mock_anomaly_alert.assert_called_once()
    call_args = mock_anomaly_alert.call_args
    assert "Anomalies detected in Pipeline" in call_args[1]["message"]
    assert "flagged" in call_args[1]["message"]
    assert "Total Anomalies" in call_args[1]["details"]
    assert "Metrics" in call_args[1]["details"]
    assert "Anomalies" in call_args[1]["details"]


@pytest.mark.anyio
async def test_anomaly_detection_throughput_result_failure(
    async_client: AsyncClient, mock_anomaly_alert
):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    response = await async_client.post(
        "/anomaly_detection_rule",
        json=TEST_ANOMALY_DETECTION_RULE_THROUGHPUT_POST_DATA,
    )
    assert response.status_code == 201

    for i in range(1, 7):
        response = await async_client.post(
            "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
        )
        execution_id = response.json()["id"]

        if (
            i == 6
        ):  # Trigger anomaly by giving ridiculous throughput (high total_rows, low duration)
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            post_data.update(
                {
                    "total_rows": 999999,
                    "end_date": pendulum.now("UTC")
                    .add(seconds=1)
                    .isoformat(),  # Very short duration
                }
            )
        else:
            # Vary the baseline data to create different throughput values
            post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
            # Vary total_rows and duration to create different throughput values
            post_data.update(
                {
                    "total_rows": 30 + (i * 5),  # 35, 40, 45, 50, 55
                    "end_date": pendulum.now("UTC")
                    .add(minutes=50 + (i * 10))
                    .isoformat(),  # 60, 70, 80, 90, 100 minutes
                }
            )

        post_data.update(
            {
                "id": response.json()["id"],
            }
        )
        response = await async_client.post("/end_pipeline_execution", json=post_data)
        assert response.status_code == 204
        # Call anomaly detection directly since background tasks don't run in tests (mocked)
        async with AsyncSessionLocal() as session:
            await db_detect_anomalies_for_pipeline_execution(
                session, pipeline_id, execution_id
            )

    mock_anomaly_alert.assert_called_once()
    call_args = mock_anomaly_alert.call_args
    assert "Anomalies detected in Pipeline" in call_args[1]["message"]
    assert "flagged" in call_args[1]["message"]
    assert "Total Anomalies" in call_args[1]["details"]
    assert "Metrics" in call_args[1]["details"]
    assert "Anomalies" in call_args[1]["details"]
