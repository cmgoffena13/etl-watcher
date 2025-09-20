#!/usr/bin/env python3
"""Test database connection speed"""

import asyncio
import time

import asyncpg
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.settings import config

console = Console()


async def test_connection_speed():
    """Test raw asyncpg connection speed"""
    console.print(
        Panel.fit(
            "[bold blue]Database Connection Speed Test[/bold blue]",
            border_style="blue",
        )
    )

    start_time = time.time()

    try:
        # Convert SQLAlchemy URL to asyncpg format
        url = config.DATABASE_URL
        if url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql+asyncpg://", "postgresql://", 1)

        conn = await asyncpg.connect(url)
        connection_time = time.time() - start_time

        # Test a simple query
        query_start = time.time()
        result = await conn.fetchval("SELECT 1")
        query_time = time.time() - query_start
        total_time = time.time() - start_time

        # Create results table
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Time", style="green", justify="right")
        table.add_column("Status", style="yellow")

        # Add rows to table
        table.add_row("Connection", f"{connection_time:.3f}s", "✅ Success")
        table.add_row("Query", f"{query_time:.3f}s", "✅ Success")
        table.add_row("Total", f"{total_time:.3f}s", "✅ Success")

        console.print("\n[bold green]Connection Speed Results[/bold green]")
        console.print(table)

        # Performance assessment
        console.print("\n[bold yellow]Performance Assessment[/bold yellow]")
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

        await conn.close()

    except Exception as e:
        console.print(f"[red]Connection failed: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(test_connection_speed())
