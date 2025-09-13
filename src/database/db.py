import logging

import pendulum
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.models import AddressType, PipelineType
from src.database.session import engine

logger = logging.getLogger(__name__)


async def create_test_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE DATABASE test"))


async def reset_database():
    logger.info("Dropping All Tables")
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        # Drop dependent tables first (tables with foreign keys)
        await conn.execute(text("DROP TABLE IF EXISTS anomaly_detection_result"))
        await conn.execute(text("DROP TABLE IF EXISTS anomaly_detection_rule"))
        await conn.execute(
            text("DROP TABLE IF EXISTS timeliness_pipeline_execution_log")
        )
        await conn.execute(text("DROP TABLE IF EXISTS freshness_pipeline_log"))
        await conn.execute(text("DROP TABLE IF EXISTS pipeline_execution"))
        await conn.execute(text("DROP TABLE IF EXISTS address_lineage_closure"))
        await conn.execute(text("DROP TABLE IF EXISTS address_lineage"))
        await conn.execute(text("DROP TABLE IF EXISTS pipeline"))
        await conn.execute(text("DROP TABLE IF EXISTS address"))
        # Drop parent tables last (tables referenced by foreign keys)
        await conn.execute(text("DROP TABLE IF EXISTS pipeline_type"))
        await conn.execute(text("DROP TABLE IF EXISTS address_type"))
        await conn.execute(text("DROP TYPE IF EXISTS datepartenum"))
        await conn.execute(text("DROP TYPE IF EXISTS anomalymetricfieldenum"))
        await conn.execute(text("DROP TYPE IF EXISTS timelinessdatepartenum"))


async def create_initial_records():
    initial_pipeline_types = [
        PipelineType(
            name="extraction",
            group_name="extraction",
            freshness_number=12,
            freshness_datepart="hour",
            mute_freshness_check=False,
        ),
        PipelineType(
            name="audit",
            group_name="audit",
            freshness_number=12,
            freshness_datepart="hour",
            mute_freshness_check=False,
        ),
        PipelineType(
            name="publish",
            group_name="publish",
            freshness_number=12,
            freshness_datepart="hour",
            mute_freshness_check=False,
        ),
    ]
    initial_address_types = [
        AddressType(name="databricks", group_name="database"),
        AddressType(name="GCS", group_name="file"),
        AddressType(name="looker", group_name="report"),
        AddressType(name="api-integration", group_name="api"),
    ]

    logger.info("Truncating Tables")
    async with engine.begin() as conn:  # Creates DB Transaction
        # Truncate dependent tables first (tables with foreign keys)
        await conn.execute(text("TRUNCATE TABLE anomaly_detection_result CASCADE"))
        await conn.execute(text("TRUNCATE TABLE anomaly_detection_rule CASCADE"))
        await conn.execute(
            text("TRUNCATE TABLE timeliness_pipeline_execution_log CASCADE")
        )
        await conn.execute(text("TRUNCATE TABLE pipeline_execution CASCADE"))
        await conn.execute(text("TRUNCATE TABLE address_lineage_closure CASCADE"))
        await conn.execute(text("TRUNCATE TABLE address_lineage CASCADE"))
        await conn.execute(text("TRUNCATE TABLE pipeline CASCADE"))
        await conn.execute(text("TRUNCATE TABLE address CASCADE"))
        # Truncate parent tables last (tables referenced by foreign keys)
        await conn.execute(text("TRUNCATE TABLE pipeline_type CASCADE"))
        await conn.execute(text("TRUNCATE TABLE address_type CASCADE"))
    logger.info("Successfully Truncated Tables")

    logger.info("Inserting Initial Records")
    async with AsyncSession(engine) as session:
        session.add_all(initial_pipeline_types)
        session.add_all(initial_address_types)
        await session.commit()
    logger.info("Successfully Inserted Records")


def _calculate_timely_time(timestamp, datepart, number):
    """Calculate the expected time based on datepart and number"""
    # Convert to pendulum if it's a regular datetime
    if hasattr(timestamp, "add"):
        timestamp = timestamp
    else:
        timestamp = pendulum.instance(timestamp)

    if datepart.upper() == "MINUTE":
        return timestamp.add(minutes=number)
    elif datepart.upper() == "HOUR":
        return timestamp.add(hours=number)
    elif datepart.upper() == "DAY":
        return timestamp.add(days=number)
    elif datepart.upper() == "WEEK":
        return timestamp.add(weeks=number)
    elif datepart.upper() == "MONTH":
        return timestamp.add(months=number)
    elif datepart.upper() == "YEAR":
        return timestamp.add(years=number)
    else:
        raise ValueError(f"Unsupported datepart: {datepart}")


def _get_display_datepart(datepart, number):
    """Convert datepart to display format (singular/plural)"""
    datepart_lower = datepart.lower()
    if number == 1:
        return datepart_lower
    else:
        return f"{datepart_lower}s"
