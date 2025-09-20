#!/usr/bin/env python3
"""Diagnose database schema and indexes"""

import asyncio

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.settings import get_database_config

console = Console()


async def check_schema_health():
    """Check database schema, indexes, and constraints"""
    console.print(
        Panel.fit(
            "[bold blue]Database Schema Diagnostics[/bold blue]", border_style="blue"
        )
    )

    # Create engine with echo disabled for clean output
    db_config = get_database_config()
    engine = create_async_engine(
        url=db_config["sqlalchemy.url"],
        echo=False,
        future=db_config["sqlalchemy.future"],
        connect_args=db_config.get("sqlalchemy.connect_args", {}),
    )

    try:
        async with engine.connect() as conn:
            # Table Sizes and Row Counts
            console.print("\n[bold green]Table Sizes and Row Counts[/bold green]")
            result = await conn.execute(
                text("""
                SELECT 
                    t.schemaname, 
                    t.tablename, 
                    pg_size_pretty(pg_total_relation_size(t.schemaname||'.'||t.tablename)) as size,
                    pg_total_relation_size(t.schemaname||'.'||t.tablename) as size_bytes,
                    n_live_tup as row_count
                FROM pg_tables t
                LEFT JOIN pg_stat_user_tables s 
                    ON t.tablename = s.relname 
                    AND t.schemaname = s.schemaname
                WHERE t.schemaname = 'public'
                ORDER BY t.tablename;
            """)
            )

            table = Table(
                show_header=True, header_style="bold magenta", box=box.ROUNDED
            )
            table.add_column("Table Name", style="cyan")
            table.add_column("Size (KB)", style="yellow", justify="right")
            table.add_column("Rows", style="blue", justify="right")

            for row in result:
                size_kb = round(row.size_bytes / 1024, 1) if row.size_bytes else 0
                row_count = row.row_count if row.row_count is not None else 0
                table.add_row(row.tablename, f"{size_kb:,} KB", f"{row_count:,}")

            console.print(table)

            # Index Usage
            console.print("\n[bold green]Index Usage[/bold green]")
            result = await conn.execute(
                text("""
                SELECT schemaname, relname as tablename, indexrelname as indexname, 
                       idx_scan, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, idx_scan DESC;
            """)
            )

            index_table = Table(
                show_header=True, header_style="bold magenta", box=box.ROUNDED
            )
            index_table.add_column("Table Name", style="cyan")
            index_table.add_column("Index Name", style="cyan")
            index_table.add_column("Scans", style="yellow", justify="right")
            index_table.add_column("Tuples Read", style="green", justify="right")

            for row in result:
                index_table.add_row(
                    row.tablename,
                    row.indexname,
                    str(row.idx_scan),
                    str(row.idx_tup_read),
                )

            console.print(index_table)

            # Potential Missing Indexes
            console.print("\n[bold yellow]Potential Missing Indexes[/bold yellow]")
            result = await conn.execute(
                text("""
                SELECT schemaname, relname as tablename, seq_scan, seq_tup_read
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public' AND seq_scan > 0
                ORDER BY seq_tup_read DESC;
            """)
            )

            rows = list(result)
            if not rows:
                console.print("[dim]No tables with sequential scans found[/dim]")
            else:
                missing_table = Table(
                    show_header=True, header_style="bold magenta", box=box.ROUNDED
                )
                missing_table.add_column("Table Name", style="cyan")
                missing_table.add_column("Seq Scans", style="red", justify="right")
                missing_table.add_column("Tuples Read", style="red", justify="right")

                significant_scans = 0
                for row in rows:
                    if row.seq_tup_read > 1000:
                        missing_table.add_row(
                            row.tablename, str(row.seq_scan), str(row.seq_tup_read)
                        )
                        significant_scans += 1

                if significant_scans == 0:
                    console.print(
                        "[dim]No tables with significant sequential scans (>1000 tuples)[/dim]"
                    )
                else:
                    console.print(missing_table)

            # Unused Indexes
            console.print(
                "\n[bold red]Unused Indexes (consider investigating)[/bold red]"
            )
            result = await conn.execute(
                text("""
                SELECT schemaname, relname as tablename, indexrelname as indexname, idx_scan
                FROM pg_stat_user_indexes 
                WHERE schemaname = 'public' AND idx_scan = 0
                ORDER BY relname;
            """)
            )

            unused_rows = list(result)
            if not unused_rows:
                console.print("[dim]No unused indexes found[/dim]")
            else:
                unused_table = Table(
                    show_header=True, header_style="bold magenta", box=box.ROUNDED
                )
                unused_table.add_column("Table", style="cyan")
                unused_table.add_column("Index Name", style="red")
                unused_table.add_column("Status", style="red")

                for row in unused_rows:
                    unused_table.add_row(row.tablename, row.indexname, "Never used")

                console.print(unused_table)

            # Table Statistics
            console.print("\n[bold green]Table Statistics[/bold green]")
            result = await conn.execute(
                text("""
                SELECT 
                schemaname, 
                relname as tablename, 
                n_tup_ins, 
                n_tup_upd, 
                n_tup_del, 
                n_live_tup, 
                n_dead_tup
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                ORDER BY n_live_tup DESC;
            """)
            )

            stats_table = Table(
                show_header=True, header_style="bold magenta", box=box.ROUNDED
            )
            stats_table.add_column("Table Name", style="cyan")
            stats_table.add_column("Live Tuples", style="green", justify="right")
            stats_table.add_column("Dead Tuples", style="red", justify="right")
            stats_table.add_column("Status", style="yellow")

            for row in result:
                status = ""
                if row.n_live_tup > 0 and row.n_dead_tup > row.n_live_tup * 0.1:
                    status = "⚠️  High dead tuple ratio"
                elif row.n_live_tup == 0 and row.n_dead_tup > 0:
                    status = "⚠️  Empty with dead tuples"
                else:
                    status = "✅ OK"

                stats_table.add_row(
                    row.tablename, str(row.n_live_tup), str(row.n_dead_tup), status
                )

            console.print(stats_table)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_schema_health())
