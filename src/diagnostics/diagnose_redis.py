import asyncio
import time
from typing import Any, Dict

import redis.asyncio as redis
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.settings import config

console = Console()


async def check_redis_health():
    """Comprehensive Redis health check"""
    console.print(
        Panel.fit(
            "[bold blue]Redis Connection Performance Test[/bold blue]",
            border_style="blue",
        )
    )

    # Test 1: Basic Redis connection
    console.print("\n[bold green]1. Basic Redis connection[/bold green]")
    start = time.time()
    try:
        if not config.REDIS_URL:
            raise ValueError("REDIS_URL is not configured")

        redis_client = redis.from_url(config.REDIS_URL, decode_responses=True)

        # Test ping
        ping_start = time.time()
        pong = await redis_client.ping()
        ping_time = (time.time() - ping_start) * 1000  # Convert to ms
        console.print(f"   [cyan]Ping time:[/cyan] {ping_time:.2f}ms")

        # Test set/get operations
        set_get_start = time.time()
        test_key = "watcher:diagnostics:test"
        test_value = f"test_value_{int(time.time())}"

        await redis_client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
        retrieved_value = await redis_client.get(test_key)
        set_get_time = (time.time() - set_get_start) * 1000  # Convert to ms
        console.print(f"   [cyan]Set/Get time:[/cyan] {set_get_time:.2f}ms")

        # Clean up test key
        await redis_client.delete(test_key)

        total_time = time.time() - start
        console.print(f"   [cyan]Total time:[/cyan] {total_time:.3f}s")

        # Performance assessment
        if ping_time < 1:
            console.print("   [green]✅ Ping speed: Excellent (<1ms)[/green]")
        elif ping_time < 5:
            console.print("   [green]✅ Ping speed: Good (1-5ms)[/green]")
        elif ping_time < 10:
            console.print("   [yellow]⚠️  Ping speed: Moderate (5-10ms)[/yellow]")
        else:
            console.print("   [red]❌ Ping speed: Slow (>10ms)[/red]")

        if set_get_time < 5:
            console.print("   [green]✅ Set/Get speed: Excellent (<5ms)[/green]")
        elif set_get_time < 10:
            console.print("   [green]✅ Set/Get speed: Good (5-10ms)[/green]")
        elif set_get_time < 20:
            console.print("   [yellow]⚠️  Set/Get speed: Moderate (10-20ms)[/yellow]")
        else:
            console.print("   [red]❌ Set/Get speed: Slow (>20ms)[/red]")

    except Exception as e:
        console.print(f"   [red]Failed: {e}[/red]")
        return

    # Test 2: Redis server information
    console.print("\n[bold green]2. Redis server information[/bold green]")
    try:
        info = await redis_client.info()

        # Display key metrics
        console.print(
            f"   [cyan]Redis version:[/cyan] {info.get('redis_version', 'Unknown')}"
        )

        # Format memory usage to show MB instead of M
        memory_human = info.get("used_memory_human", "Unknown")
        memory_used_bytes = info.get("used_memory", 0)
        memory_max_bytes = info.get("maxmemory", 0)

        if memory_human != "Unknown" and memory_human.endswith("M"):
            memory_mb = memory_human.replace("M", "MB")
            console.print(f"   [cyan]Memory used:[/cyan] {memory_mb}")
        else:
            console.print(f"   [cyan]Memory used:[/cyan] {memory_human}")

        # Show memory usage percentage if maxmemory is set
        if memory_max_bytes > 0:
            memory_percent = (memory_used_bytes / memory_max_bytes) * 100
            console.print(
                f"   [cyan]Memory usage:[/cyan] {memory_percent:.1f}% of limit"
            )

            if memory_percent > 90:
                console.print("   [red]❌ Memory usage: Critical (>90%)[/red]")
            elif memory_percent > 80:
                console.print("   [yellow]⚠️  Memory usage: High (80-90%)[/yellow]")
            elif memory_percent > 60:
                console.print("   [yellow]⚠️  Memory usage: Moderate (60-80%)[/yellow]")
            else:
                console.print("   [green]✅ Memory usage: Good (<60%)[/green]")
        else:
            console.print("   [cyan]Memory limit:[/cyan] No limit set")

        console.print(
            f"   [cyan]Connected clients:[/cyan] {info.get('connected_clients', 'Unknown')}"
        )
        console.print(
            f"   [cyan]Commands processed:[/cyan] {info.get('total_commands_processed', 'Unknown')}"
        )

        # Format uptime nicely
        uptime_seconds = info.get("uptime_in_seconds", 0)
        if uptime_seconds > 86400:  # More than a day
            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            console.print(f"   [cyan]Uptime:[/cyan] {days}d {hours}h")
        elif uptime_seconds > 3600:  # More than an hour
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            console.print(f"   [cyan]Uptime:[/cyan] {hours}h {minutes}m")
        else:
            minutes = uptime_seconds // 60
            seconds = uptime_seconds % 60
            console.print(f"   [cyan]Uptime:[/cyan] {minutes}m {seconds}s")

    except Exception as e:
        console.print(f"   [red]Failed: {e}[/red]")

    # Test 3: Multiple operations test
    console.print("\n[bold green]3. Multiple operations test[/bold green]")
    try:
        start = time.time()
        tasks = []

        async def test_operation(i):
            op_start = time.time()
            test_key = f"watcher:diagnostics:test_{i}"
            test_value = f"test_value_{i}_{int(time.time())}"

            await redis_client.set(test_key, test_value, ex=60)
            await redis_client.get(test_key)
            await redis_client.delete(test_key)

            return time.time() - op_start

        # Run 5 concurrent operations
        for i in range(5):
            tasks.append(test_operation(i))

        times = await asyncio.gather(*tasks)
        total_time = time.time() - start

        console.print(
            f"   [cyan]Individual operation times:[/cyan] {[f'{t * 1000:.2f}ms' for t in times]}"
        )
        console.print(f"   [cyan]Total time for 5 operations:[/cyan] {total_time:.3f}s")
        console.print(
            f"   [cyan]Average per operation:[/cyan] {sum(times) / len(times) * 1000:.2f}ms"
        )

        avg_time = sum(times) / len(times) * 1000
        if avg_time < 5:
            console.print(
                "   [green]✅ Concurrent performance: Excellent (<5ms avg)[/green]"
            )
        elif avg_time < 10:
            console.print(
                "   [green]✅ Concurrent performance: Good (5-10ms avg)[/green]"
            )
        elif avg_time < 20:
            console.print(
                "   [yellow]⚠️  Concurrent performance: Moderate (10-20ms avg)[/yellow]"
            )
        else:
            console.print("   [red]❌ Concurrent performance: Slow (>20ms avg)[/red]")

    except Exception as e:
        console.print(f"   [red]Failed: {e}[/red]")

    await redis_client.close()
