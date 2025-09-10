import pendulum
import pytest
from fastapi import Response
from sqlmodel import select

from src.database.models.pipeline import Pipeline
from src.database.models.pipeline_type import PipelineType
from src.database.timeliness_utils import db_check_pipeline_timeliness
from src.tests.fixtures.pipeline import TEST_PIPELINE_TIMELINESS_DATA
from src.tests.fixtures.pipeline_type import TEST_PIPELINE_TYPE_POST_DATA
from src.types import DatePartEnum


class TestTimelinessUtils:
    """Test timeliness utility functions using existing fixtures."""

    @pytest.fixture
    async def pipeline_type_fixture(self, db_session):
        """Create pipeline type from existing fixture."""
        pipeline_type = PipelineType(**TEST_PIPELINE_TYPE_POST_DATA)
        db_session.add(pipeline_type)
        await db_session.commit()
        await db_session.refresh(pipeline_type)
        return pipeline_type

    @pytest.fixture
    async def pipeline_on_time(self, db_session, pipeline_type_fixture):
        """Create pipeline that should pass timeliness check."""
        # Use fixture data but update timestamps to be within threshold
        one_hour_ago = pendulum.now("UTC").subtract(hours=1)

        pipeline_data = TEST_PIPELINE_TIMELINESS_DATA.copy()
        pipeline_data.update(
            {
                "pipeline_type_id": pipeline_type_fixture.id,
                "last_target_insert": one_hour_ago,
                "last_target_update": one_hour_ago,
                "last_target_soft_delete": one_hour_ago,
            }
        )

        pipeline = Pipeline(**pipeline_data)
        db_session.add(pipeline)
        await db_session.commit()
        await db_session.refresh(pipeline)
        return pipeline

    @pytest.fixture
    async def pipeline_late(self, db_session, pipeline_type_fixture):
        """Create pipeline that should fail timeliness check."""
        # Use fixture data but update timestamps to be beyond threshold
        three_hours_ago = pendulum.now("UTC").subtract(hours=3)

        pipeline_data = TEST_PIPELINE_TIMELINESS_DATA.copy()
        pipeline_data.update(
            {
                "pipeline_type_id": pipeline_type_fixture.id,
                "name": "Late Pipeline",
                "last_target_insert": three_hours_ago,
                "last_target_update": three_hours_ago,
                "last_target_soft_delete": three_hours_ago,
            }
        )

        pipeline = Pipeline(**pipeline_data)
        db_session.add(pipeline)
        await db_session.commit()
        await db_session.refresh(pipeline)
        return pipeline

    @pytest.fixture
    async def pipeline_muted(self, db_session, pipeline_type_fixture):
        """Create pipeline that should be skipped due to muting."""
        three_hours_ago = pendulum.now("UTC").subtract(hours=3)

        pipeline_data = TEST_PIPELINE_TIMELINESS_DATA.copy()
        pipeline_data.update(
            {
                "pipeline_type_id": pipeline_type_fixture.id,
                "name": "Muted Pipeline",
                "last_target_insert": three_hours_ago,
                "last_target_update": three_hours_ago,
                "last_target_soft_delete": three_hours_ago,
                "mute_timely_check": True,
            }
        )

        pipeline = Pipeline(**pipeline_data)
        db_session.add(pipeline)
        await db_session.commit()
        await db_session.refresh(pipeline)
        return pipeline

    @pytest.mark.asyncio
    async def test_timeliness_check_success(self, db_session, pipeline_on_time):
        """Test timeliness check when pipeline passes."""
        # This should not raise an exception
        try:
            await db_check_pipeline_timeliness(db_session)
        except Exception as e:
            pytest.fail(f"Timeliness check should not fail: {e}")

    @pytest.mark.asyncio
    async def test_timeliness_check_failure(self, db_session, pipeline_late):
        """Test timeliness check when pipeline fails."""
        with pytest.raises(Exception) as exc_info:
            await db_check_pipeline_timeliness(db_session)

        # Verify the error message contains expected information
        error_message = str(exc_info.value)
        assert "Late Pipeline" in error_message
        assert "failed timeliness check" in error_message

    @pytest.mark.asyncio
    async def test_timeliness_check_muted_pipeline(self, db_session, pipeline_muted):
        """Test that muted pipelines are skipped."""
        # Should pass because muted pipeline is skipped
        try:
            await db_check_pipeline_timeliness(db_session)
        except Exception as e:
            pytest.fail(f"Timeliness check should pass with muted pipeline: {e}")

    @pytest.mark.asyncio
    async def test_timeliness_check_mixed_scenario(
        self, db_session, pipeline_on_time, pipeline_late, pipeline_muted
    ):
        """Test timeliness check with mix of passing, failing, and muted pipelines."""
        with pytest.raises(Exception) as exc_info:
            await db_check_pipeline_timeliness(db_session)

        # Should fail due to the late pipeline, but muted pipeline should be ignored
        error_message = str(exc_info.value)
        assert "Late Pipeline" in error_message
        assert "Muted Pipeline" not in error_message  # Muted should be skipped
