#!/usr/bin/env python3
"""Diagnose database performance, deadlocks, and active queries"""

import asyncio

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.settings import config

console = Console()


async def check_performance_health():
    """Check database performance, deadlocks, and active queries"""
    console.print(
        Panel.fit(
            "[bold blue]Database Performance Diagnostics[/bold blue]",
            border_style="blue",
        )
    )

    engine = create_async_engine(
        config.DATABASE_URL, pool_size=1, max_overflow=0, pool_timeout=5
    )

    try:
        async with engine.connect() as conn:
            # Deadlock Statistics
            console.print("\n[bold red]Deadlock Statistics[/bold red]")
            result = await conn.execute(
                text("""
                SELECT 
                    datname as database_name,
                    deadlocks,
                    EXTRACT(EPOCH FROM (NOW() - stats_reset)) / 86400 as days_since_reset
                FROM pg_stat_database 
                WHERE datname = current_database()
                ORDER BY deadlocks DESC;
            """)
            )

            deadlock_table = Table(
                show_header=True, header_style="bold red", box=box.ROUNDED
            )
            deadlock_table.add_column("Database", style="cyan")
            deadlock_table.add_column("Deadlocks", style="red", justify="right")
            deadlock_table.add_column(
                "Days Since Reset", style="purple", justify="right"
            )
            deadlock_table.add_column("Status", style="yellow")

            for row in result:
                status = ""
                if row.deadlocks > 0:
                    if row.deadlocks > 10:
                        status = "🚨 High deadlock count"
                    elif row.deadlocks > 5:
                        status = "⚠️  Moderate deadlock count"
                    else:
                        status = "⚠️  Some deadlocks detected"
                else:
                    status = "✅ No deadlocks"

                days_reset = int(row.days_since_reset) if row.days_since_reset else 0

                deadlock_table.add_row(
                    row.database_name, str(row.deadlocks), str(days_reset), status
                )

            console.print(deadlock_table)

            # Currently Locked Tables
            console.print("\n[bold red]Currently Locked Tables[/bold red]")
            result = await conn.execute(
                text("""
                SELECT 
                    relation::regclass as table_name,
                    mode,
                    COUNT(*) as lock_count
                FROM pg_locks l
                JOIN pg_class c ON l.relation = c.oid
                JOIN pg_namespace n ON c.relnamespace = n.oid
                WHERE l.relation IS NOT NULL
                AND n.nspname = 'public'
                GROUP BY l.relation, mode
                ORDER BY lock_count DESC, table_name;
            """)
            )

            locked_rows = list(result)
            if not locked_rows:
                console.print("[dim]No tables currently locked[/dim]")
            else:
                locked_table = Table(
                    show_header=True, header_style="bold red", box=box.ROUNDED
                )
                locked_table.add_column("Table Name", style="cyan")
                locked_table.add_column("Lock Mode", style="yellow")
                locked_table.add_column("Count", style="red", justify="right")

                for row in locked_rows:
                    locked_table.add_row(
                        str(row.table_name), row.mode, str(row.lock_count)
                    )

                console.print(locked_table)

            # Top Active Queries
            console.print("\n[bold green]Top Active Queries[/bold green]")
            result = await conn.execute(
                text("""
                SELECT 
                    pid,
                    state,
                    query_start,
                    EXTRACT(EPOCH FROM (NOW() - query_start)) as duration_seconds,
                    LEFT(query, 100) as query_preview,
                    wait_event_type,
                    wait_event
                FROM pg_stat_activity 
                WHERE state != 'idle' 
                AND query NOT LIKE '%pg_stat_activity%'
                ORDER BY query_start;
            """)
            )

            query_rows = list(result)
            if not query_rows:
                console.print("[dim]No active queries found[/dim]")
            else:
                query_table = Table(
                    show_header=True, header_style="bold green", box=box.ROUNDED
                )
                query_table.add_column("PID", style="cyan", justify="right")
                query_table.add_column("State", style="yellow")
                query_table.add_column("Duration (s)", style="red", justify="right")
                query_table.add_column("Wait Event", style="purple")
                query_table.add_column("Query Preview", style="white")

                for row in query_rows:
                    duration = (
                        round(row.duration_seconds, 1) if row.duration_seconds else 0
                    )
                    wait_info = (
                        f"{row.wait_event_type}: {row.wait_event}"
                        if row.wait_event_type
                        else "None"
                    )

                    query_table.add_row(
                        str(row.pid),
                        row.state,
                        str(duration),
                        wait_info,
                        row.query_preview,
                    )

                console.print(query_table)

            # Long Running Queries
            console.print("\n[bold yellow]Long Running Queries (>30s)[/bold yellow]")
            result = await conn.execute(
                text("""
                SELECT 
                    pid,
                    state,
                    query_start,
                    EXTRACT(EPOCH FROM (NOW() - query_start)) as duration_seconds,
                    LEFT(query, 80) as query_preview
                FROM pg_stat_activity 
                WHERE state != 'idle' 
                AND EXTRACT(EPOCH FROM (NOW() - query_start)) > 30
                AND query NOT LIKE '%pg_stat_activity%'
                ORDER BY duration_seconds DESC;
            """)
            )

            long_query_rows = list(result)
            if not long_query_rows:
                console.print("[dim]No long running queries found[/dim]")
            else:
                long_query_table = Table(
                    show_header=True, header_style="bold yellow", box=box.ROUNDED
                )
                long_query_table.add_column("PID", style="cyan", justify="right")
                long_query_table.add_column("State", style="yellow")
                long_query_table.add_column(
                    "Duration (s)", style="red", justify="right"
                )
                long_query_table.add_column("Query Preview", style="white")

                for row in long_query_rows:
                    duration = round(row.duration_seconds, 1)

                    long_query_table.add_row(
                        str(row.pid), row.state, str(duration), row.query_preview
                    )

                console.print(long_query_table)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_performance_health())
