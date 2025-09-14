#!/usr/bin/env python3
"""Test database connection speed"""

import asyncio
import time

import asyncpg

from src.settings import config


async def test_connection_speed():
    """Test raw asyncpg connection speed"""
    start_time = time.time()

    try:
        # Convert SQLAlchemy URL to asyncpg format
        url = config.DATABASE_URL
        if url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql+asyncpg://", "postgresql://", 1)

        conn = await asyncpg.connect(url)
        connection_time = time.time() - start_time

        print(f"Raw asyncpg connection time: {connection_time:.3f}s")

        # Test a simple query
        query_start = time.time()
        result = await conn.fetchval("SELECT 1")
        query_time = time.time() - query_start

        print(f"Simple query time: {query_time:.3f}s")
        print(f"Total time: {time.time() - start_time:.3f}s")

        await conn.close()

    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection_speed())
