#!/usr/bin/env python3
"""Diagnose Celery workers and task performance"""

import asyncio
import json

import redis
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.celery_app import celery
from src.settings import config

console = Console()


async def check_celery_health():
    """Check Celery workers, task performance, and queue health"""
    console.print(
        Panel.fit(
            "[bold blue]Celery Workers & Task Performance[/bold blue]",
            border_style="blue",
        )
    )

    try:
        # Worker Statistics
        console.print("\n[bold green]Active Workers[/bold green]")
        try:
            inspect = celery.control.inspect(timeout=1)
            stats = inspect.stats()

            if not stats:
                console.print("[yellow]No active workers found[/yellow]")
            else:
                worker_table = Table(
                    show_header=True, header_style="bold green", box=box.ROUNDED
                )
                worker_table.add_column("Worker", style="cyan")
                worker_table.add_column("Status", style="yellow")
                worker_table.add_column("Pool Size", style="blue", justify="right")
                worker_table.add_column("Memory Usage", style="purple")

                for worker_name, worker_stats in stats.items():
                    pool_info = worker_stats.get("pool", {})
                    rusage = worker_stats.get("rusage", {})

                    memory_mb = (
                        rusage.get("maxrss", 0) / 1024 if rusage.get("maxrss") else 0
                    )

                    worker_table.add_row(
                        worker_name,
                        "Active",
                        str(pool_info.get("max-concurrency", "N/A")),
                        f"{memory_mb:.1f} MB" if memory_mb > 0 else "N/A",
                    )

                console.print(worker_table)

        except Exception as e:
            console.print(f"[red]Failed to get worker stats: {e}[/red]")

        # Queue Information
        console.print("\n[bold yellow]Queue Information[/bold yellow]")
        try:
            redis_client = redis.Redis.from_url(config.REDIS_URL)

            redis_table = Table(
                show_header=True, header_style="bold cyan", box=box.ROUNDED
            )
            redis_table.add_column("Queue", style="cyan")
            redis_table.add_column("Tasks in Queue", style="green", justify="right")
            redis_table.add_column("Scheduled", style="blue", justify="right")
            redis_table.add_column("Status", style="yellow")

            # Only check the celery queue since that's where the actual tasks are
            queue_name = "celery"
            queued_count = redis_client.llen(queue_name)
            scheduled_count = redis_client.zcard(f"{queue_name}:scheduled")

            # Determine status based on queue depth (same thresholds as alert system)
            if queued_count >= 100:
                status = "🚨 Critical"
            elif queued_count >= 50:
                status = "⚠️  Warning"
            elif queued_count > 0:
                status = "ℹ️  Low"
            else:
                status = "✅ Empty"

            redis_table.add_row(
                queue_name, str(queued_count), str(scheduled_count), status
            )

            console.print(redis_table)

        except Exception as redis_e:
            console.print(f"[yellow]Redis check failed: {redis_e}[/yellow]")

        # Worker Activity Summary
        console.print("\n[bold magenta]Worker Activity Summary[/bold magenta]")
        try:
            stats = inspect.stats()
            if not stats:
                console.print("[dim]No worker stats available[/dim]")
            else:
                activity_table = Table(
                    show_header=True, header_style="bold magenta", box=box.ROUNDED
                )
                activity_table.add_column("Worker", style="cyan")
                activity_table.add_column(
                    "Tasks Completed", style="green", justify="right"
                )
                activity_table.add_column("Tasks Failed", style="red", justify="right")
                activity_table.add_column(
                    "Currently Active", style="yellow", justify="right"
                )

                for worker_name, worker_stats in stats.items():
                    total_tasks = worker_stats.get("total", {})
                    completed = sum(total_tasks.values()) if total_tasks else 0

                    # Get failed tasks count
                    failed_tasks = worker_stats.get("failed", {})
                    failed = sum(failed_tasks.values()) if failed_tasks else 0

                    # Get currently active tasks for this worker
                    active_tasks = inspect.active()
                    active_count = 0
                    if active_tasks and worker_name in active_tasks:
                        active_count = len(active_tasks[worker_name])

                    activity_table.add_row(
                        worker_name,
                        str(completed),
                        str(failed),
                        str(active_count),
                    )

                console.print(activity_table)

        except Exception as e:
            console.print(f"[red]Failed to get worker activity: {e}[/red]")

        # Currently Active Tasks
        console.print("\n[bold cyan]Currently Active Tasks[/bold cyan]")
        try:
            active_tasks = inspect.active()
            if not active_tasks:
                console.print(
                    "[dim]No active tasks found (tasks processing too fast to catch)[/dim]"
                )
            else:
                active_table = Table(
                    show_header=True, header_style="bold cyan", box=box.ROUNDED
                )
                active_table.add_column("Worker", style="cyan")
                active_table.add_column("Task Name", style="green")
                active_table.add_column("Task ID", style="blue")

                for worker_name, tasks in active_tasks.items():
                    for task in tasks:
                        task_name = task.get("name", "Unknown")
                        task_id = task.get("id", "Unknown")

                        active_table.add_row(worker_name, task_name, task_id)

                console.print(active_table)

        except Exception as e:
            console.print(f"[red]Failed to get active tasks: {e}[/red]")

        # Scheduled Tasks
        console.print("\n[bold yellow]Scheduled Tasks[/bold yellow]")
        try:
            scheduled_tasks = inspect.scheduled()
            if not scheduled_tasks:
                console.print("[dim]No scheduled tasks found[/dim]")
            else:
                scheduled_table = Table(
                    show_header=True, header_style="bold yellow", box=box.ROUNDED
                )
                scheduled_table.add_column("Worker", style="cyan")
                scheduled_table.add_column("Task Name", style="green")
                scheduled_table.add_column("ETA", style="blue")
                scheduled_table.add_column("Priority", style="purple")

                for worker_name, tasks in scheduled_tasks.items():
                    for task in tasks:
                        task_name = task.get("name", "Unknown")
                        eta = task.get("eta", "Unknown")
                        priority = task.get("priority", "Unknown")

                        scheduled_table.add_row(
                            worker_name, task_name, str(eta), str(priority)
                        )

                console.print(scheduled_table)

        except Exception as e:
            console.print(f"[red]Failed to get scheduled tasks: {e}[/red]")

        # Task Performance Summary
        console.print("\n[bold blue]Task Performance Summary[/bold blue]")
        try:
            # Get aggregated task averages from Redis
            task_averages = redis_client.hgetall("celery_task_averages")

            if not task_averages:
                console.print(
                    "No task performance data found (tasks may need to be restarted to capture duration)"
                )
            else:
                task_table = Table()
                task_table.add_column("Task Name", header_style="bold blue")
                task_table.add_column(
                    "Avg Duration", header_style="bold blue", justify="right"
                )
                task_table.add_column(
                    "Total Executions", header_style="bold blue", justify="right"
                )

                task_durations = []
                total_executions = 0

                for task_name_bytes, avg_data_bytes in task_averages.items():
                    task_name = task_name_bytes.decode()
                    avg_data = avg_data_bytes.decode()

                    try:
                        avg_duration, count = avg_data.split(",")
                        avg_duration = float(avg_duration)
                        count = int(count)

                        # Clean up task name for display
                        display_name = (
                            task_name.split(".")[-1].replace("_", " ").title()
                        )

                        task_table.add_row(
                            display_name, f"{avg_duration * 1000:.1f}ms", str(count)
                        )

                        task_durations.append(avg_duration)
                        total_executions += count

                    except (ValueError, IndexError) as e:
                        console.print(f"  Error parsing data for {task_name}: {e}")
                        continue

                console.print(task_table)

                if task_durations:
                    console.print("\n[bold blue]Task Overall Summary[/bold blue]")
                    overall_avg = sum(task_durations) / len(task_durations)
                    min_avg = min(task_durations)
                    max_avg = max(task_durations)

                    # Create summary table
                    summary_table = Table()
                    summary_table.add_column("Metric", header_style="bold blue")
                    summary_table.add_column(
                        "Value", header_style="bold blue", justify="right"
                    )

                    summary_table.add_row(
                        "Task types with data", str(len(task_durations))
                    )
                    summary_table.add_row("Total executions", str(total_executions))
                    summary_table.add_row(
                        "Average across all types", f"{overall_avg * 1000:.1f}ms"
                    )
                    summary_table.add_row(
                        "Fastest task type", f"{min_avg * 1000:.1f}ms"
                    )
                    summary_table.add_row(
                        "Slowest task type", f"{max_avg * 1000:.1f}ms"
                    )

                    console.print(summary_table)

        except Exception as e:
            console.print(f"[red]Failed to get task performance data: {e}[/red]")

    except Exception as e:
        console.print(f"[red]Celery diagnostic failed: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(check_celery_health())
