import io
import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from rich.console import Console

import src.diagnostics.diagnose_celery as celery_module
import src.diagnostics.diagnose_connection as conn_module
import src.diagnostics.diagnose_performance as perf_module
import src.diagnostics.diagnose_redis as redis_module
import src.diagnostics.diagnose_schema as schema_module
from src.diagnostics.diagnose_celery import check_celery_health
from src.diagnostics.diagnose_connection import test_connection_scenarios
from src.diagnostics.diagnose_performance import check_performance_health
from src.diagnostics.diagnose_redis import check_redis_health
from src.diagnostics.diagnose_schema import check_schema_health

router = APIRouter()


@router.get("/diagnostics", include_in_schema=False)
async def get_diagnostics_page():
    """Serve the diagnostics HTML page"""
    try:
        with open("src/templates/diagnostics.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Diagnostics page not found</h1>", status_code=404
        )


async def capture_rich_output(func, module):
    """Capture Rich console output and convert to HTML"""
    output_buffer = io.StringIO()

    console = Console(file=output_buffer, width=200, force_terminal=True)

    module.console = console

    await func()

    output = output_buffer.getvalue()

    # Convert Rich markup to HTML
    html_output = convert_rich_to_html(output)

    return html_output


def convert_rich_to_html(text):
    """Convert Rich console output to HTML with proper styling"""
    # An AI Mess
    html = text

    # Handle complex Rich styling sequences
    # Bold + Color combinations
    html = re.sub(
        r"\x1b\[1;35m(.*?)\x1b\[0m",
        r'<span style="font-weight: bold; color: #e91e63;">\1</span>',
        html,
    )  # Bold magenta (table headers)
    html = re.sub(
        r"\x1b\[1;36m(.*?)\x1b\[0m",
        r'<span style="font-weight: bold; color: #00bcd4;">\1</span>',
        html,
    )  # Bold cyan
    html = re.sub(
        r"\x1b\[1;32m(.*?)\x1b\[0m",
        r'<span style="font-weight: bold; color: #4caf50;">\1</span>',
        html,
    )  # Bold green
    html = re.sub(
        r"\x1b\[1;33m(.*?)\x1b\[0m",
        r'<span style="font-weight: bold; color: #ff9800;">\1</span>',
        html,
    )  # Bold yellow
    html = re.sub(
        r"\x1b\[1;31m(.*?)\x1b\[0m",
        r'<span style="font-weight: bold; color: #f44336;">\1</span>',
        html,
    )  # Bold red
    html = re.sub(
        r"\x1b\[1;34m(.*?)\x1b\[0m",
        r'<span style="font-weight: bold; color: #2196f3;">\1</span>',
        html,
    )  # Bold blue

    # Bold text
    html = re.sub(
        r"\x1b\[1m(.*?)\x1b\[0m", r'<span style="font-weight: bold;">\1</span>', html
    )

    # Colors - Green
    html = re.sub(
        r"\x1b\[32m(.*?)\x1b\[0m", r'<span style="color: #4caf50;">\1</span>', html
    )
    html = re.sub(
        r"\x1b\[92m(.*?)\x1b\[0m", r'<span style="color: #4caf50;">\1</span>', html
    )  # Bright green

    # Colors - Red
    html = re.sub(
        r"\x1b\[31m(.*?)\x1b\[0m", r'<span style="color: #f44336;">\1</span>', html
    )
    html = re.sub(
        r"\x1b\[91m(.*?)\x1b\[0m", r'<span style="color: #f44336;">\1</span>', html
    )  # Bright red

    # Colors - Yellow/Orange
    html = re.sub(
        r"\x1b\[33m(.*?)\x1b\[0m", r'<span style="color: #ff9800;">\1</span>', html
    )
    html = re.sub(
        r"\x1b\[93m(.*?)\x1b\[0m", r'<span style="color: #ff9800;">\1</span>', html
    )  # Bright yellow

    # Colors - Blue
    html = re.sub(
        r"\x1b\[34m(.*?)\x1b\[0m", r'<span style="color: #2196f3;">\1</span>', html
    )
    html = re.sub(
        r"\x1b\[94m(.*?)\x1b\[0m", r'<span style="color: #2196f3;">\1</span>', html
    )  # Bright blue

    # Colors - Cyan
    html = re.sub(
        r"\x1b\[36m(.*?)\x1b\[0m", r'<span style="color: #00bcd4;">\1</span>', html
    )
    html = re.sub(
        r"\x1b\[96m(.*?)\x1b\[0m", r'<span style="color: #00bcd4;">\1</span>', html
    )  # Bright cyan

    # Colors - Magenta
    html = re.sub(
        r"\x1b\[35m(.*?)\x1b\[0m", r'<span style="color: #e91e63;">\1</span>', html
    )
    html = re.sub(
        r"\x1b\[95m(.*?)\x1b\[0m", r'<span style="color: #e91e63;">\1</span>', html
    )  # Bright magenta

    # Colors - White (for headers)
    html = re.sub(
        r"\x1b\[37m(.*?)\x1b\[0m", r'<span style="color: #ffffff;">\1</span>', html
    )
    html = re.sub(
        r"\x1b\[97m(.*?)\x1b\[0m", r'<span style="color: #ffffff;">\1</span>', html
    )  # Bright white

    # Colors - Black
    html = re.sub(
        r"\x1b\[30m(.*?)\x1b\[0m", r'<span style="color: #000000;">\1</span>', html
    )

    # Dim text
    html = re.sub(
        r"\x1b\[2m(.*?)\x1b\[0m", r'<span style="opacity: 0.7;">\1</span>', html
    )

    # Italic text
    html = re.sub(
        r"\x1b\[3m(.*?)\x1b\[0m", r'<span style="font-style: italic;">\1</span>', html
    )

    # Underline text
    html = re.sub(
        r"\x1b\[4m(.*?)\x1b\[0m",
        r'<span style="text-decoration: underline;">\1</span>',
        html,
    )

    # Remove any remaining ANSI escape codes
    ansi_escape = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    html = ansi_escape.sub("", html)

    # Convert checkmarks and symbols
    html = re.sub(r"✅", '<span style="color: #4caf50;">✅</span>', html)
    html = re.sub(r"⚠️", '<span style="color: #ff9800;">⚠️</span>', html)
    html = re.sub(r"❌", '<span style="color: #f44336;">❌</span>', html)

    # Convert newlines to <br> but preserve table structure
    html = html.replace("\n", "<br>")

    # Wrap the entire output in a monospace div to preserve table alignment
    html = f'<div style="font-family: monospace; white-space: pre-wrap;">{html}</div>'

    return html


@router.get("/diagnostics/connection-performance", include_in_schema=False)
async def get_diagnostics_connection_performance():
    """Get comprehensive connection performance diagnostics"""
    try:
        output = await capture_rich_output(test_connection_scenarios, conn_module)
        return {"status": "success", "output": output, "type": "connection_performance"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Connection performance test failed: {str(e)}"
        )


@router.get("/diagnostics/schema-health", include_in_schema=False)
async def get_diagnostics_schema_health():
    """Get database schema health diagnostics"""
    try:
        output = await capture_rich_output(check_schema_health, schema_module)
        return {"status": "success", "output": output, "type": "schema_health"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Schema health check failed: {str(e)}"
        )


@router.get("/diagnostics/performance", include_in_schema=False)
async def get_diagnostics_performance():
    """Get database performance diagnostics"""
    try:
        output = await capture_rich_output(check_performance_health, perf_module)
        return {"status": "success", "output": output, "type": "performance"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Performance diagnostics failed: {str(e)}"
        )


@router.get("/diagnostics/celery", include_in_schema=False)
async def get_diagnostics_celery():
    """Get Celery workers and task performance diagnostics"""
    try:
        output = await capture_rich_output(check_celery_health, celery_module)
        return {"status": "success", "output": output, "type": "celery"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Celery diagnostics failed: {str(e)}"
        )


@router.get("/diagnostics/redis", include_in_schema=False)
async def get_diagnostics_redis():
    """Get Redis connection and health diagnostics"""
    try:
        output = await capture_rich_output(check_redis_health, redis_module)
        return {"status": "success", "output": output, "type": "redis"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Redis diagnostics failed: {str(e)}"
        )
