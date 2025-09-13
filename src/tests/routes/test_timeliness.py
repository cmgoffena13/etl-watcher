import pytest
from httpx import AsyncClient

from src.tests.fixtures.pipeline import (
    TEST_PIPELINE_POST_DATA,
)
from src.tests.fixtures.pipeline_execution import (
    TEST_PIPELINE_EXECUTION_END_DATA,
    TEST_PIPELINE_EXECUTION_START_DATA,
)


@pytest.mark.anyio
async def test_timeliness_pipeline_execution_failure(
    async_client: AsyncClient, mock_slack_notifications
):
    response = await async_client.post("/pipeline", json=TEST_PIPELINE_POST_DATA)
    assert response.status_code == 201

    response = await async_client.post(
        "/start_pipeline_execution", json=TEST_PIPELINE_EXECUTION_START_DATA
    )
    assert response.status_code == 201

    post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
    post_data.update(
        {
            "end_date": "2025-09-08T21:07:43.824220+00:00",
        }
    )

    response = await async_client.post("/end_pipeline_execution", json=post_data)
    assert response.status_code == 204

    response = await async_client.post("/timeliness")
    assert response.status_code == 201

    mock_slack_notifications.assert_called_once()
    call_args = mock_slack_notifications.call_args
    assert (
        "pipeline execution(s) exceeding timeliness threshold"
        in call_args[1]["message"]
    )
    assert "Threshold (seconds)" in call_args[1]["details"]
    assert "Affected Pipelines" in call_args[1]["details"]
