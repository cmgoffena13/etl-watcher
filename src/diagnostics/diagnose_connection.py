#!/usr/bin/env python3
"""Diagnose database connection performance"""

import asyncio
import socket
import time

import asyncpg
from rich.console import Console
from rich.panel import Panel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.settings import config

console = Console()


async def test_connection_scenarios():
    """Test different connection scenarios"""
    console.print(
        Panel.fit(
            "[bold blue]Database Connection Performance Test[/bold blue]",
            border_style="blue",
        )
    )

    # Test 1: Raw asyncpg connection
    console.print("\n[bold green]1. Raw asyncpg connection[/bold green]")
    start = time.time()
    try:
        url = config.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(url)
        connection_time = time.time() - start
        console.print(f"   [cyan]Connection time:[/cyan] {connection_time:.3f}s")

        # Test query
        query_start = time.time()
        result = await conn.fetchval("SELECT 1")
        query_time = time.time() - query_start
        console.print(f"   [cyan]Query time:[/cyan] {query_time:.3f}s")

        await conn.close()
        total_time = time.time() - start
        console.print(f"   [cyan]Total time:[/cyan] {total_time:.3f}s")

        # Performance assessment
        if connection_time < 0.1:
            console.print("   [green]✅ Connection speed: Excellent (<100ms)[/green]")
        elif connection_time < 0.5:
            console.print("   [yellow]⚠️  Connection speed: Good (100-500ms)[/yellow]")
        else:
            console.print("   [red]❌ Connection speed: Slow (>500ms)[/red]")

        if query_time < 0.01:
            console.print("   [green]✅ Query speed: Excellent (<10ms)[/green]")
        elif query_time < 0.05:
            console.print("   [yellow]⚠️  Query speed: Good (10-50ms)[/yellow]")
        else:
            console.print("   [red]❌ Query speed: Slow (>50ms)[/red]")
    except Exception as e:
        console.print(f"   [red]Failed: {e}[/red]")

    # Test 2: SQLAlchemy engine (first connection)
    console.print("\n[bold green]2. SQLAlchemy engine (first connection)[/bold green]")
    start = time.time()
    try:
        engine = create_async_engine(
            config.DATABASE_URL, pool_size=1, max_overflow=0, pool_timeout=5
        )

        async with engine.connect() as conn:
            connection_time = time.time() - start
            console.print(f"   [cyan]Connection time:[/cyan] {connection_time:.3f}s")

            # Test query
            query_start = time.time()
            await conn.execute(text("SELECT 1"))
            query_time = time.time() - query_start
            console.print(f"   [cyan]Query time:[/cyan] {query_time:.3f}s")

        total_time = time.time() - start
        console.print(f"   [cyan]Total time:[/cyan] {total_time:.3f}s")

        # Performance assessment
        if connection_time < 0.1:
            console.print("   [green]✅ Connection speed: Excellent (<100ms)[/green]")
        elif connection_time < 0.5:
            console.print("   [yellow]⚠️  Connection speed: Good (100-500ms)[/yellow]")
        else:
            console.print("   [red]❌ Connection speed: Slow (>500ms)[/red]")

        if query_time < 0.01:
            console.print("   [green]✅ Query speed: Excellent (<10ms)[/green]")
        elif query_time < 0.05:
            console.print("   [yellow]⚠️  Query speed: Good (10-50ms)[/yellow]")
        else:
            console.print("   [red]❌ Query speed: Slow (>50ms)[/red]")
    except Exception as e:
        console.print(f"   [red]Failed: {e}[/red]")

    # Test 3: SQLAlchemy engine (second connection from pool)
    console.print(
        "\n[bold green]3. SQLAlchemy engine (second connection from pool)[/bold green]"
    )
    start = time.time()
    try:
        async with engine.connect() as conn:
            connection_time = time.time() - start
            console.print(f"   [cyan]Connection time:[/cyan] {connection_time:.3f}s")

            # Test query
            query_start = time.time()
            await conn.execute(text("SELECT 1"))
            query_time = time.time() - query_start
            console.print(f"   [cyan]Query time:[/cyan] {query_time:.3f}s")

        total_time = time.time() - start
        console.print(f"   [cyan]Total time:[/cyan] {total_time:.3f}s")

        # Performance assessment
        if connection_time < 0.1:
            console.print("   [green]✅ Connection speed: Excellent (<100ms)[/green]")
        elif connection_time < 0.5:
            console.print("   [yellow]⚠️  Connection speed: Good (100-500ms)[/yellow]")
        else:
            console.print("   [red]❌ Connection speed: Slow (>500ms)[/red]")

        if query_time < 0.01:
            console.print("   [green]✅ Query speed: Excellent (<10ms)[/green]")
        elif query_time < 0.05:
            console.print("   [yellow]⚠️  Query speed: Good (10-50ms)[/yellow]")
        else:
            console.print("   [red]❌ Query speed: Slow (>50ms)[/red]")
    except Exception as e:
        console.print(f"   [red]Failed: {e}[/red]")

    # Test 4: Multiple rapid connections
    console.print(
        "\n[bold green]4. Multiple rapid connections (pool behavior)[/bold green]"
    )
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

        console.print(
            f"   [cyan]Individual connection times:[/cyan] {[f'{t:.3f}s' for t in times]}"
        )
        console.print(
            f"   [cyan]Total time for 5 connections:[/cyan] {total_time:.3f}s"
        )
        console.print(
            f"   [cyan]Average per connection:[/cyan] {sum(times) / len(times):.3f}s"
        )
    except Exception as e:
        console.print(f"   [red]Failed: {e}[/red]")

    # Test 5: Check if it's DNS resolution
    console.print("\n[bold green]5. Testing DNS vs IP resolution[/bold green]")
    try:
        # Extract host from URL
        url_parts = config.DATABASE_URL.split("://")[1].split("@")[1].split("/")[0]
        if ":" in url_parts:
            host, port = url_parts.split(":")
        else:
            host, port = url_parts, "5432"

        console.print(f"   [cyan]Database host:[/cyan] {host}")

        # Test DNS resolution time
        dns_start = time.time()
        ip = socket.gethostbyname(host)
        dns_time = time.time() - dns_start
        console.print(f"   [cyan]DNS resolution time:[/cyan] {dns_time:.3f}s")
        console.print(f"   [cyan]Resolved to IP:[/cyan] {ip}")

        if dns_time > 0.1:
            console.print(
                "   [yellow]⚠️  DNS resolution is slow - consider using IP address[/yellow]"
            )
        else:
            console.print("   [green]✅ DNS resolution is fast[/green]")

    except Exception as e:
        console.print(f"   [red]DNS test failed: {e}[/red]")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection_scenarios())
