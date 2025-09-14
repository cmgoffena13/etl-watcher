#!/usr/bin/env python3
"""Diagnose database connection performance"""

import asyncio
import time

import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.settings import config


async def test_connection_scenarios():
    """Test different connection scenarios"""
    print("=== Database Connection Performance Test ===\n")

    # Test 1: Raw asyncpg connection
    print("1. Raw asyncpg connection:")
    start = time.time()
    try:
        url = config.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(url)
        connection_time = time.time() - start
        print(f"   Connection time: {connection_time:.3f}s")

        # Test query
        query_start = time.time()
        result = await conn.fetchval("SELECT 1")
        query_time = time.time() - query_start
        print(f"   Query time: {query_time:.3f}s")

        await conn.close()
        print(f"   Total time: {time.time() - start:.3f}s\n")
    except Exception as e:
        print(f"   Failed: {e}\n")

    # Test 2: SQLAlchemy engine (first connection)
    print("2. SQLAlchemy engine (first connection):")
    start = time.time()
    try:
        engine = create_async_engine(
            config.DATABASE_URL, pool_size=1, max_overflow=0, pool_timeout=5
        )

        async with engine.connect() as conn:
            connection_time = time.time() - start
            print(f"   Connection time: {connection_time:.3f}s")

            # Test query
            query_start = time.time()
            await conn.execute(text("SELECT 1"))
            query_time = time.time() - query_start
            print(f"   Query time: {query_time:.3f}s")

        print(f"   Total time: {time.time() - start:.3f}s\n")
    except Exception as e:
        print(f"   Failed: {e}\n")

    # Test 3: SQLAlchemy engine (second connection from pool)
    print("3. SQLAlchemy engine (second connection from pool):")
    start = time.time()
    try:
        async with engine.connect() as conn:
            connection_time = time.time() - start
            print(f"   Connection time: {connection_time:.3f}s")

            # Test query
            query_start = time.time()
            await conn.execute(text("SELECT 1"))
            query_time = time.time() - query_start
            print(f"   Query time: {query_time:.3f}s")

        print(f"   Total time: {time.time() - start:.3f}s\n")
    except Exception as e:
        print(f"   Failed: {e}\n")

    # Test 4: Multiple rapid connections
    print("4. Multiple rapid connections (pool behavior):")
    start = time.time()
    try:
        tasks = []
        for i in range(5):

            async def test_conn(i):
                conn_start = time.time()
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                return time.time() - conn_start

            tasks.append(test_conn(i))

        times = await asyncio.gather(*tasks)
        total_time = time.time() - start

        print(f"   Individual connection times: {[f'{t:.3f}s' for t in times]}")
        print(f"   Total time for 5 connections: {total_time:.3f}s")
        print(f"   Average per connection: {sum(times) / len(times):.3f}s\n")
    except Exception as e:
        print(f"   Failed: {e}\n")

    # Test 5: Check if it's DNS resolution
    print("5. Testing DNS vs IP resolution:")
    try:
        # Extract host from URL
        url_parts = config.DATABASE_URL.split("://")[1].split("@")[1].split("/")[0]
        if ":" in url_parts:
            host, port = url_parts.split(":")
        else:
            host, port = url_parts, "5432"

        print(f"   Database host: {host}")

        # Test DNS resolution time
        import socket

        dns_start = time.time()
        ip = socket.gethostbyname(host)
        dns_time = time.time() - dns_start
        print(f"   DNS resolution time: {dns_time:.3f}s")
        print(f"   Resolved to IP: {ip}")

        if dns_time > 0.1:
            print("   ⚠️  DNS resolution is slow - consider using IP address")
        else:
            print("   ✅ DNS resolution is fast")

    except Exception as e:
        print(f"   DNS test failed: {e}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection_scenarios())
