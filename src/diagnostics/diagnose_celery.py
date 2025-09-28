#!/usr/bin/env python3
"""Diagnose Celery workers and task performance"""

import asyncio

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.celery_app import celery

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
                worker_table.add_column("Tasks/Min", style="green", justify="right")
                worker_table.add_column("Pool Size", style="blue", justify="right")
                worker_table.add_column("Memory Usage", style="purple")

                for worker_name, worker_stats in stats.items():
                    pool_info = worker_stats.get("pool", {})
                    rusage = worker_stats.get("rusage", {})

                    # Calculate tasks per minute from total tasks
                    total_tasks = worker_stats.get("total", {})
                    total_task_count = sum(total_tasks.values()) if total_tasks else 0

                    # Estimate tasks per minute (rough calculation)
                    uptime_hours = (
                        rusage.get("utime", 0) / 3600 if rusage.get("utime") else 1
                    )
                    tasks_per_minute = (
                        (total_task_count / (uptime_hours * 60))
                        if uptime_hours > 0
                        else 0
                    )

                    memory_mb = (
                        rusage.get("maxrss", 0) / 1024 if rusage.get("maxrss") else 0
                    )

                    worker_table.add_row(
                        worker_name,
                        "Active",
                        f"{tasks_per_minute:.1f}",
                        str(pool_info.get("max-concurrency", "N/A")),
                        f"{memory_mb:.1f} MB" if memory_mb > 0 else "N/A",
                    )

                console.print(worker_table)

        except Exception as e:
            console.print(f"[red]Failed to get worker stats: {e}[/red]")

        # Queue Information
        console.print("\n[bold yellow]Queue Information[/bold yellow]")
        try:
            active_queues = inspect.active_queues()
            scheduled_tasks = inspect.scheduled()
            reserved_tasks = inspect.reserved()

            if not active_queues:
                console.print("[yellow]No queue information available[/yellow]")
            else:
                queue_table = Table(
                    show_header=True, header_style="bold yellow", box=box.ROUNDED
                )
                queue_table.add_column("Queue", style="cyan")
                queue_table.add_column("Workers", style="green", justify="right")
                queue_table.add_column("Scheduled", style="blue", justify="right")
                queue_table.add_column("Reserved", style="purple", justify="right")
                queue_table.add_column("Status", style="yellow")

                queue_data = {}
                for worker_name, queues in active_queues.items():
                    for queue_info in queues:
                        queue_name = queue_info.get("name", "default")
                        if queue_name not in queue_data:
                            queue_data[queue_name] = {
                                "workers": 0,
                                "scheduled": 0,
                                "reserved": 0,
                            }
                        queue_data[queue_name]["workers"] += 1

                # Add scheduled and reserved counts
                if scheduled_tasks:
                    for worker_name, tasks in scheduled_tasks.items():
                        for queue_name in queue_data.keys():
                            queue_data[queue_name]["scheduled"] += len(
                                [
                                    t
                                    for t in tasks
                                    if t.get("delivery_info", {}).get("routing_key")
                                    == queue_name
                                ]
                            )

                if reserved_tasks:
                    for worker_name, tasks in reserved_tasks.items():
                        for queue_name in queue_data.keys():
                            queue_data[queue_name]["reserved"] += len(
                                [
                                    t
                                    for t in tasks
                                    if t.get("delivery_info", {}).get("routing_key")
                                    == queue_name
                                ]
                            )

                for queue_name, data in queue_data.items():
                    total_pending = data["scheduled"] + data["reserved"]
                    status = (
                        "Healthy"
                        if total_pending < 100
                        else "Backed Up"
                        if total_pending < 500
                        else "Critical"
                    )

                    queue_table.add_row(
                        queue_name,
                        str(data["workers"]),
                        str(data["scheduled"]),
                        str(data["reserved"]),
                        status,
                    )

                console.print(queue_table)

        except Exception as e:
            console.print(f"[red]Failed to get queue information: {e}[/red]")

        # Active Tasks
        console.print("\n[bold magenta]Currently Active Tasks[/bold magenta]")
        try:
            active_tasks = inspect.active()
            if not active_tasks:
                console.print("[dim]No active tasks found[/dim]")
            else:
                active_table = Table(
                    show_header=True, header_style="bold magenta", box=box.ROUNDED
                )
                active_table.add_column("Worker", style="cyan")
                active_table.add_column("Task Name", style="green")
                active_table.add_column("Task ID", style="blue")
                active_table.add_column("Args", style="yellow")

                for worker_name, tasks in active_tasks.items():
                    for task in tasks:
                        task_name = task.get("name", "Unknown")
                        task_id = task.get("id", "Unknown")
                        args = (
                            str(task.get("args", []))[:50] + "..."
                            if len(str(task.get("args", []))) > 50
                            else str(task.get("args", []))
                        )

                        active_table.add_row(worker_name, task_name, task_id, args)

                console.print(active_table)

        except Exception as e:
            console.print(f"[red]Failed to get active tasks: {e}[/red]")

        # Scheduled Tasks
        console.print("\n[bold yellow]Scheduled Tasks[/bold yellow]")
        try:
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

    except Exception as e:
        console.print(f"[red]Celery diagnostic failed: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(check_celery_health())
