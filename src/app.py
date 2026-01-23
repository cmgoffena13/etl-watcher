from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from rich import panel, print
from scalar_fastapi import get_scalar_api_reference

from src.database.db import setup_reporting
from src.database.session import engine, test_connection
from src.logging_conf import configure_logging
from src.middleware import register_profiling_middleware
from src.routes import (
    address_lineage_router,
    address_router,
    address_type_router,
    anomaly_detection_router,
    celery_router,
    diagnostics_router,
    freshness_router,
    lineage_graph_router,
    log_cleanup_router,
    pipeline_execution_router,
    pipeline_router,
    pipeline_type_router,
    reporting_router,
    timeliness_router,
)
from src.settings import config
from src.types import ORJSONResponse

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(panel.Panel("Server is starting up...", border_style="green"))
    configure_logging()
    await test_connection()
    await setup_reporting()
    yield
    print(panel.Panel("Server is shutting down...", border_style="red"))
    await engine.dispose()


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
FastAPIInstrumentor.instrument_app(
    app=app, excluded_urls="/health,/scalar", client_request_hook=None
)
SQLAlchemyInstrumentor().instrument(angine=engine, enable_commenter=True)


register_profiling_middleware(app, enabled=config.PROFILING_ENABLED)
app.include_router(pipeline_router)
app.include_router(pipeline_type_router)
app.include_router(pipeline_execution_router)
app.include_router(address_type_router)
app.include_router(address_router)
app.include_router(address_lineage_router)
app.include_router(lineage_graph_router)
app.include_router(timeliness_router)
app.include_router(anomaly_detection_router)
app.include_router(log_cleanup_router)
app.include_router(freshness_router)
app.include_router(celery_router)
app.include_router(diagnostics_router)
app.include_router(reporting_router)


@app.get("/")
async def heartbeat():
    return {"status": "ok"}


@app.get("/scalar", include_in_schema=False)
async def get_scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Scalar API")
