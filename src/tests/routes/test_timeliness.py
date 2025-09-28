import pendulum
import pytest
from httpx import AsyncClient

from src.database.timeliness_utils import db_check_pipeline_execution_timeliness
from src.tests.conftest import AsyncSessionLocal
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
    # Create pipeline with timeliness settings
    pipeline_data = TEST_PIPELINE_POST_DATA.copy()
    pipeline_data.update(
        {
            "timeliness_number": 1,
            "timeliness_datepart": "minute",
            "mute_timeliness_check": False,
        }
    )

    response = await async_client.post("/pipeline", json=pipeline_data)
    assert response.status_code == 201

    # Use current timestamps for the execution
    start_data = TEST_PIPELINE_EXECUTION_START_DATA.copy()
    start_data.update(
        {"start_date": pendulum.now("UTC").subtract(minutes=10).isoformat()}
    )

    response = await async_client.post("/start_pipeline_execution", json=start_data)
    assert response.status_code == 201

    post_data = TEST_PIPELINE_EXECUTION_END_DATA.copy()
    post_data.update(
        {
            "end_date": pendulum.now("UTC").add(minutes=5).isoformat(),
        }
    )

    response = await async_client.post("/end_pipeline_execution", json=post_data)
    assert response.status_code == 204

    async with AsyncSessionLocal() as session:
        await db_check_pipeline_execution_timeliness(session, None, 60)

    mock_slack_notifications.assert_called_once()
    call_args = mock_slack_notifications.call_args
    assert "Pipeline Execution Timeliness Check" in call_args[1]["message"]
    assert "Failed Executions" in call_args[1]["details"]
