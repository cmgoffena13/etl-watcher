import logging

import pendulum
from sqlalchemy import text

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
