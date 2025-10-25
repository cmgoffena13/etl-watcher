from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import text

from src.database.lineage_graph_utils import db_get_lineage_graph
from src.database.session import SessionDep
from src.models.lineage_graph import LineageGraphResponse

router = APIRouter()


@router.get(
    "/lineage-graph/", response_model=LineageGraphResponse, include_in_schema=False
)
async def get_lineage_graph(
    session: SessionDep,
    source_address_id: int,
) -> LineageGraphResponse:
    """Get lineage graph data filtered by source address."""

    try:
        return await db_get_lineage_graph(
            session=session,
            source_address_id=source_address_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving lineage graph: {str(e)}"
        )


@router.post("/lineage-graph/refresh", include_in_schema=False)
async def refresh_lineage_graph_view(session: SessionDep):
    """Refresh the lineage graph materialized view"""
    try:
        await session.exec(text("REFRESH MATERIALIZED VIEW lineage_graph_report;"))
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


@router.get("/lineage-graph", response_class=HTMLResponse, include_in_schema=False)
async def get_lineage_graph_page():
    """Serve the lineage graph HTML page."""
    try:
        with open("src/templates/lineage_graph.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Lineage graph page not found</h1>", status_code=404
        )
