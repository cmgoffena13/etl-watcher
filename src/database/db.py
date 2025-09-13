import logging

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
