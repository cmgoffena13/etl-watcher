import math
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import text

from src.database.session import SessionDep
from src.settings import config

router = APIRouter()


@router.get("/reporting", response_class=HTMLResponse, include_in_schema=False)
async def reporting_dashboard(request: Request):
    """Daily pipeline metrics reporting dashboard"""
    try:
        with open("src/templates/reporting.html", "r") as f:
            html_content = f.read()

        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Reporting dashboard not found</h1>", status_code=404
        )


@router.get("/reporting/daily-pipeline-metrics", include_in_schema=False)
async def get_daily_pipeline_metrics(
    session: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    pipeline_name: Optional[str] = Query(None),
    pipeline_type_name: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=30),
):
    """Get daily pipeline metrics with pagination and filtering"""

    # Build the query with filters
    where_clause = f"WHERE date_recorded >= CURRENT_DATE - INTERVAL '{days} DAY'"
    params = {"offset": (page - 1) * page_size, "limit": page_size}

    if pipeline_name:
        where_clause += " AND pipeline_name = :pipeline_name"
        params["pipeline_name"] = pipeline_name

    if pipeline_type_name:
        where_clause += " AND pipeline_type_name = :pipeline_type_name"
        params["pipeline_type_name"] = pipeline_type_name

    # Get total count for pagination
    count_query = text(f"""
        SELECT COUNT(*) as total
        FROM daily_pipeline_report
        {where_clause}
    """)

    total_result = await session.exec(count_query, params=params)
    total_records = total_result.scalar_one()
    total_pages = math.ceil(total_records / page_size)

    # Get the data
    data_query = text(f"""
            SELECT 
                date_recorded,
                pipeline_name,
                pipeline_type_name,
                total_executions,
                failed_executions,
                error_percentage,
                daily_inserts,
                daily_updates,
                daily_soft_deletes,
                daily_total_rows,
                avg_duration_seconds,
                daily_throughput
            FROM daily_pipeline_report
            {where_clause}
            ORDER BY date_recorded DESC, pipeline_name ASC
            LIMIT :limit OFFSET :offset
        """)

    result = await session.exec(data_query, params=params)
    records = result.fetchall()

    # Convert to list of dicts for JSON response
    data = []
    for record in records:
        data.append(
            {
                "date_recorded": record.date_recorded.isoformat()
                if record.date_recorded
                else None,
                "pipeline_name": record.pipeline_name,
                "pipeline_type_name": record.pipeline_type_name,
                "total_executions": record.total_executions,
                "failed_executions": record.failed_executions,
                "error_percentage": float(record.error_percentage)
                if record.error_percentage
                else 0.0,
                "daily_inserts": record.daily_inserts or 0,
                "daily_updates": record.daily_updates or 0,
                "daily_soft_deletes": record.daily_soft_deletes or 0,
                "daily_total_rows": record.daily_total_rows or 0,
                "avg_duration_seconds": float(record.avg_duration_seconds)
                if record.avg_duration_seconds
                else 0.0,
                "daily_throughput": float(record.daily_throughput)
                if record.daily_throughput
                else 0.0,
            }
        )

    return {
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }


@router.get("/reporting/pipeline-names", include_in_schema=False)
async def get_pipeline_names(
    session: SessionDep, pipeline_type_name: Optional[str] = Query(None)
):
    """Get list of pipeline names for dropdown, optionally filtered by pipeline type"""
    where_clause = ""
    params = {}

    if pipeline_type_name:
        where_clause = "WHERE pipeline_type_name = :pipeline_type_name"
        params["pipeline_type_name"] = pipeline_type_name

    query = text(f"""
        SELECT DISTINCT pipeline_name 
        FROM daily_pipeline_report 
        {where_clause}
        ORDER BY pipeline_name
    """)

    result = await session.exec(query, params=params)
    pipeline_names = [row.pipeline_name for row in result.fetchall()]

    return {"pipeline_names": pipeline_names}


@router.get("/reporting/pipeline-type-names", include_in_schema=False)
async def get_pipeline_type_names(session: SessionDep):
    """Get list of pipeline type names for dropdown"""
    query = text("""
        SELECT DISTINCT pipeline_type_name 
        FROM daily_pipeline_report 
        ORDER BY pipeline_type_name
    """)

    result = await session.exec(query)
    pipeline_type_names = [row.pipeline_type_name for row in result.fetchall()]

    return {"pipeline_type_names": pipeline_type_names}


@router.post("/reporting/refresh", include_in_schema=False)
async def refresh_materialized_view(session: SessionDep):
    """Refresh the daily pipeline report materialized view"""
    try:
        await session.exec(text("REFRESH MATERIALIZED VIEW daily_pipeline_report;"))
        await session.commit()
        return {
            "status": "success",
            "message": "Materialized view refreshed successfully",
        }
    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": f"Failed to refresh materialized view: {str(e)}",
        }
