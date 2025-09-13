import pendulum
import pytest
from httpx import AsyncClient

from src.tests.fixtures.pipeline import TEST_PIPELINE_POST_DATA
from src.tests.fixtures.pipeline_execution import (
    TEST_PIPELINE_EXECUTION_END_DATA,
    TEST_PIPELINE_EXECUTION_START_DATA,
)


@pytest.mark.anyio
async def test_log_cleanup(async_client: AsyncClient):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201

    retention_date = pendulum.now("UTC").subtract(days=95).isoformat()
    post_data = TEST_PIPELINE_EXECUTION_START_DATA.copy()
    post_data.update({"start_date": retention_date})

    response = await async_client.post("/start_pipeline_execution", json=post_data)
    assert response.status_code == 201
    response = await async_client.post("/log_cleanup", json={"retention_days": 90})
    assert response.status_code == 200
    assert response.json() == {
        "total_pipeline_executions_deleted": 1,
        "total_timeliness_pipeline_execution_logs_deleted": 0,
        "total_anomaly_detection_results_deleted": 0,
    }
