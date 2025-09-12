import pendulum
import pytest
from httpx import AsyncClient
from sqlmodel import Session

from src.database.models.pipeline import Pipeline
from src.database.models.pipeline_type import PipelineType
from src.tests.fixtures.pipeline import (
    TEST_PIPELINE_POST_DATA,
    TEST_PIPELINE_TIMELINESS_DATA,
)
from src.tests.fixtures.pipeline_execution import (
    TEST_PIPELINE_EXECUTION_END_DATA,
    TEST_PIPELINE_EXECUTION_START_DATA,
)
from src.tests.fixtures.pipeline_type import TEST_PIPELINE_TYPE_POST_DATA


@pytest.mark.anyio
async def test_timeliness_check_success(async_client: AsyncClient):
    """Test timeliness check when pipeline passes."""
    # Create pipeline type
    await async_client.post("/pipeline_type", json=TEST_PIPELINE_TYPE_POST_DATA)

    # Create pipeline with timestamps within threshold
    one_hour_ago = pendulum.now("UTC").subtract(hours=1)
    pipeline_data = TEST_PIPELINE_TIMELINESS_DATA.copy()
    pipeline_data.update(
        {
            "last_target_insert": one_hour_ago.isoformat(),
            "last_target_update": one_hour_ago.isoformat(),
            "last_target_soft_delete": one_hour_ago.isoformat(),
            "timely_number": 2,
            "timely_datepart": "hour",
        }
    )

    await async_client.post("/pipeline", json=pipeline_data)

    # This should not raise an exception
    response = await async_client.post("/timeliness")
    assert response.status_code == 201


@pytest.mark.anyio
async def test_timeliness_check_muted_pipeline(async_client: AsyncClient):
    """Test that muted pipelines are skipped."""
    # Create pipeline type
    await async_client.post("/pipeline_type", json=TEST_PIPELINE_TYPE_POST_DATA)

    # Create muted pipeline with timestamps beyond threshold
    three_hours_ago = pendulum.now("UTC").subtract(hours=3)
    pipeline_data = TEST_PIPELINE_TIMELINESS_DATA.copy()
    pipeline_data.update(
        {
            "name": "Muted Pipeline",
            "last_target_insert": three_hours_ago.isoformat(),
            "last_target_update": three_hours_ago.isoformat(),
            "last_target_soft_delete": three_hours_ago.isoformat(),
            "timely_number": 1,
            "timely_datepart": "hour",
            "mute_timely_check": True,
        }
    )

    await async_client.post("/pipeline", json=pipeline_data)

    # Should pass because muted pipeline is skipped
    response = await async_client.post("/timeliness")
    assert response.status_code == 201


@pytest.mark.anyio
async def test_timeliness_pipeline_check_failure(
    async_client: AsyncClient, db_session: Session, mock_slack_notifications
):
    """Test timeliness check when pipeline fails."""

    # Create pipeline type manually
    pipeline_type = PipelineType(
        name="audit",
        group_name="databricks",
        timely_number=12,
        timely_datepart="hour",
        mute_timely_check=False,
    )
    db_session.add(pipeline_type)
    await db_session.flush()  # Get the ID without committing

    twelve_hours_ago = pendulum.now("UTC").subtract(hours=12)
    pipeline = Pipeline(
        name="Late Pipeline",
        pipeline_type_id=pipeline_type.id,
        last_target_insert=twelve_hours_ago,
        last_target_update=twelve_hours_ago,
        last_target_soft_delete=twelve_hours_ago,
        timely_number=1,
        timely_datepart="hour",
        mute_timely_check=False,
    )

    db_session.add(pipeline)
    await db_session.commit()

    response = await async_client.post("/timeliness")
    assert response.status_code in [200, 201]
    response_data = response.json()
    assert response_data["status"] == "warning"

    mock_slack_notifications.assert_called_once()
    call_args = mock_slack_notifications.call_args
    assert "Pipeline Timeliness Check Failed" in call_args[1]["message"]
    assert "Late Pipeline" in call_args[1]["details"]["Failed Pipelines"]


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
