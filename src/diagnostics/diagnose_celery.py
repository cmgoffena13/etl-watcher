#!/usr/bin/env python3
"""Diagnose Celery workers and task performance"""

import asyncio
import json

import pendulum
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

        # Initialize variables
        redis_client = None

        # Queue Information
        console.print("\n[bold yellow]Queue Information[/bold yellow]")
        try:
            redis_client = redis.Redis.from_url(config.REDIS_URL)

            redis_table = Table(
                show_header=True, header_style="bold cyan", box=box.ROUNDED
            )
            redis_table.add_column("Queue", style="cyan")
            redis_table.add_column("Tasks in Queue", style="green", justify="right")
            redis_table.add_column("Status", style="yellow")

            # Check both celery and scheduled queues
            queues_to_check = ["celery", "scheduled"]

            for queue_name in queues_to_check:
                queued_count = redis_client.llen(queue_name)

                # Determine status based on queue depth (same thresholds as alert system)
                if queued_count >= 100:
                    status = "🚨 Critical"
                elif queued_count >= 50:
                    status = "⚠️  Warning"
                elif queued_count > 0:
                    status = "ℹ️  Low"
                else:
                    status = "✅ Empty"

                redis_table.add_row(queue_name, str(queued_count), status)

            console.print(redis_table)

        except Exception as redis_e:
            console.print(f"[yellow]Redis check failed: {redis_e}[/yellow]")

        # Scheduled Tasks
        console.print("\n[bold magenta]Scheduled Tasks[/bold magenta]")
        console.print("[bold]Beat Schedule Configuration:[/bold]")
        console.print(
            f"  [cyan]Freshness Check:[/cyan] {config.WATCHER_FRESHNESS_CHECK_SCHEDULE}"
        )
        console.print(
            f"  [cyan]Timeliness Check:[/cyan] {config.WATCHER_TIMELINESS_CHECK_SCHEDULE}"
        )
        console.print(
            f"  [cyan]Celery Queue Health Check:[/cyan] {config.WATCHER_CELERY_QUEUE_HEALTH_CHECK_SCHEDULE}"
        )

        # Queue Analysis
        console.print("\n[bold green]Queue Analysis[/bold green]")
        try:
            if redis_client is None:
                console.print(
                    "[yellow]Redis client not available - skipping queue analysis[/yellow]"
                )
                return

            # Check both regular and scheduled queues
            regular_queue = "celery"
            scheduled_queue = "scheduled"

            # Get messages from both queues
            regular_messages = redis_client.lrange(regular_queue, 0, -1)
            scheduled_messages = redis_client.lrange(scheduled_queue, 0, -1)

            # Count tasks by type for both queues
            task_counts = {
                "detect_anomalies_task": 0,
                "timeliness_check_task": 0,
                "freshness_check_task": 0,
                "address_lineage_closure_rebuild_task": 0,
                "pipeline_execution_closure_maintain_task": 0,
                "scheduled_freshness_check": 0,
                "scheduled_timeliness_check": 0,
                "scheduled_celery_queue_health_check": 0,
                "unknown": 0,
            }

            # Analyze regular queue messages
            for message in regular_messages:
                try:
                    task_data = json.loads(message)

                    # Task name is in headers.task, not at the root level
                    headers = task_data.get("headers", {})
                    task_name = headers.get("task", "unknown")

                    # Map task names to our known tasks
                    if "detect_anomalies_task" in task_name:
                        task_counts["detect_anomalies_task"] += 1
                    elif "timeliness_check_task" in task_name:
                        task_counts["timeliness_check_task"] += 1
                    elif "freshness_check_task" in task_name:
                        task_counts["freshness_check_task"] += 1
                    elif "address_lineage_closure_rebuild_task" in task_name:
                        task_counts["address_lineage_closure_rebuild_task"] += 1
                    elif "pipeline_execution_closure_maintain_task" in task_name:
                        task_counts["pipeline_execution_closure_maintain_task"] += 1
                    else:
                        task_counts["unknown"] += 1
                except (json.JSONDecodeError, KeyError):
                    task_counts["unknown"] += 1

            # Analyze scheduled queue messages
            for message in scheduled_messages:
                try:
                    task_data = json.loads(message)

                    # Task name is in headers.task, not at the root level
                    headers = task_data.get("headers", {})
                    task_name = headers.get("task", "unknown")

                    # Map scheduled task names
                    if "scheduled_freshness_check" in task_name:
                        task_counts["scheduled_freshness_check"] += 1
                    elif "scheduled_timeliness_check" in task_name:
                        task_counts["scheduled_timeliness_check"] += 1
                    elif "scheduled_celery_queue_health_check" in task_name:
                        task_counts["scheduled_celery_queue_health_check"] += 1
                    else:
                        task_counts["unknown"] += 1
                except (json.JSONDecodeError, KeyError):
                    task_counts["unknown"] += 1

            # Create queue analysis table
            breakdown_table = Table(
                show_header=True, header_style="bold green", box=box.ROUNDED
            )
            breakdown_table.add_column("Task Type", style="cyan")
            breakdown_table.add_column("Count", style="green", justify="right")
            breakdown_table.add_column("Percentage", style="blue", justify="right")

            total_tasks = sum(task_counts.values())

            # Show queue summary
            console.print(
                f"[green]Regular queue: {len(regular_messages)} tasks[/green]"
            )
            console.print(
                f"[blue]Scheduled queue: {len(scheduled_messages)} tasks[/blue]"
            )
            console.print(f"[yellow]Total: {total_tasks} tasks[/yellow]")
            console.print()

            if total_tasks > 0:
                for task_name, count in task_counts.items():
                    if count > 0:
                        # Convert snake_case to readable format with custom mappings
                        readable_name = task_name.replace("_", " ").title()

                        # Custom mappings for better readability
                        if task_name == "scheduled_celery_queue_health_check":
                            readable_name = "Scheduled Celery Queue Health Check"
                        elif task_name == "scheduled_freshness_check":
                            readable_name = "Scheduled Freshness Check"
                        elif task_name == "scheduled_timeliness_check":
                            readable_name = "Scheduled Timeliness Check"

                        percentage = (
                            (count / total_tasks * 100) if total_tasks > 0 else 0
                        )
                        breakdown_table.add_row(
                            readable_name, str(count), f"{percentage:.1f}%"
                        )

                console.print(breakdown_table)
            else:
                console.print("[dim]No tasks currently in queue[/dim]")

        except Exception as e:
            console.print(f"[yellow]Queue analysis failed: {e}[/yellow]")

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
                overall_durations = []  # For overall summary, excludes trigger tasks
                overall_executions = 0

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

                        # For overall summary, skip scheduled tasks that are just triggers
                        if not task_name.endswith(
                            "scheduled_freshness_check"
                        ) and not task_name.endswith("scheduled_timeliness_check"):
                            overall_durations.append(avg_duration)
                            overall_executions += count

                    except (ValueError, IndexError) as e:
                        console.print(f"  Error parsing data for {task_name}: {e}")
                        continue

                console.print(task_table)

                if overall_durations:
                    console.print("\n[bold blue]Task Overall Summary[/bold blue]")
                    console.print(
                        "[dim]Note: scheduled_freshness_check and scheduled_timeliness_check are excluded as they are just triggers that queue other tasks[/dim]"
                    )
                    overall_avg = sum(overall_durations) / len(overall_durations)
                    min_avg = min(overall_durations)
                    max_avg = max(overall_durations)

                    # Create summary table
                    summary_table = Table()
                    summary_table.add_column("Metric", header_style="bold blue")
                    summary_table.add_column(
                        "Value", header_style="bold blue", justify="right"
                    )

                    summary_table.add_row(
                        "Task types with data", str(len(overall_durations))
                    )
                    summary_table.add_row("Total executions", str(overall_executions))
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
