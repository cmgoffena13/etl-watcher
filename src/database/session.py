import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import text
from sqlmodel.ext.asyncio.session import AsyncSession

from src.settings import get_database_config

logger = logging.getLogger(__name__)

db_config = get_database_config()
engine = create_async_engine(
    url=db_config["sqlalchemy.url"],
    echo=db_config["sqlalchemy.echo"],
    future=db_config["sqlalchemy.future"],
    connect_args=db_config.get("sqlalchemy.connect_args", {}),
)


async def test_connection():
    logger.info("Testing Database Connection")
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Test Successful")
    except Exception as e:
        logger.critical(f"Database Connection Failed: {e}")
        raise


async def get_session():
    async with sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
