import logging
from pathlib import Path

import pendulum
from sqlalchemy import text

from src.database.session import engine

logger = logging.getLogger(__name__)


async def create_test_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE DATABASE test"))


async def truncate_tables():
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    """
                    TRUNCATE TABLE 
                    anomaly_detection_result,
                    anomaly_detection_rule,
                    timeliness_pipeline_execution_log,
                    pipeline_execution,
                    address_lineage_closure,
                    address_lineage,
                    pipeline,
                    address,
                    pipeline_type,
                    address_type
                    RESTART IDENTITY CASCADE
                    """
                )
            )
    except Exception as e:
        print(f"Warning: Failed to truncate tables: {e}")


async def reset_database():
    logger.info("Dropping All Tables")
    async with engine.begin() as conn:
        # Drop materialized views FIRST (before any dependent tables)
        await conn.execute(
            text("DROP MATERIALIZED VIEW IF EXISTS daily_pipeline_report")
        )
        # Drop dependent tables (tables with foreign keys)
        await conn.execute(text("DROP TABLE IF EXISTS anomaly_detection_result"))
        await conn.execute(text("DROP TABLE IF EXISTS anomaly_detection_rule"))
        await conn.execute(
            text("DROP TABLE IF EXISTS timeliness_pipeline_execution_log")
        )
        await conn.execute(text("DROP TABLE IF EXISTS freshness_pipeline_log"))
        await conn.execute(text("DROP TABLE IF EXISTS pipeline_execution"))
        await conn.execute(text("DROP TABLE IF EXISTS address_lineage_closure"))
        # Drop tables in dependency order
        await conn.execute(text("DROP TABLE IF EXISTS address_lineage"))
        await conn.execute(text("DROP TABLE IF EXISTS pipeline"))
        await conn.execute(text("DROP TABLE IF EXISTS address"))
        # Drop parent tables last (tables referenced by foreign keys)
        await conn.execute(text("DROP TABLE IF EXISTS pipeline_type"))
        await conn.execute(text("DROP TABLE IF EXISTS address_type"))
        # Drop alembic version table
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        # Drop custom types last
        await conn.execute(text("DROP TYPE IF EXISTS datepartenum"))
        await conn.execute(text("DROP TYPE IF EXISTS anomalymetricfieldenum"))


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


async def setup_reporting():
    async with engine.begin() as conn:
        reporting_folder = Path(__file__).parent.parent / "reporting"

        if not reporting_folder.exists():
            logger.warning(f"Reporting folder not found: {reporting_folder}")
            return

        for sql_file in reporting_folder.glob("*.sql"):
            try:
                logger.info(f"Executing {sql_file.name}...")

                with open(sql_file, "r") as f:
                    sql_content = f.read().strip()

                if sql_content:
                    statements = [
                        stmt.strip() for stmt in sql_content.split(";") if stmt.strip()
                    ]

                    for i, statement in enumerate(statements):
                        try:
                            logger.info(
                                f"  Executing statement {i + 1}/{len(statements)}..."
                            )
                            await conn.execute(text(statement))
                        except Exception as e:
                            logger.error(f"  Failed to execute statement {i + 1}: {e}")
                            logger.error(f"  Statement: {statement[:200]}...")
                            raise
                    logger.info(f"Successfully executed {sql_file.name}")
                else:
                    logger.warning(f"{sql_file.name} is empty, skipping")

            except Exception as e:
                logger.error(f"Failed to execute {sql_file.name}: {e}")
                raise

        logger.info("Reporting setup complete")
