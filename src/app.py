import logging
from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI
from rich import panel, print
from scalar_fastapi import get_scalar_api_reference

from src.database.db import reset_database
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
    log_cleanup_router,
    pipeline_execution_router,
    pipeline_router,
    pipeline_type_router,
    timeliness_router,
)
from src.settings import config
from src.types import ORJSONResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(panel.Panel("Server is starting up...", border_style="green"))
    configure_logging()
    await test_connection()
    # await reset_database()
    yield
    print(panel.Panel("Server is shutting down...", border_style="red"))
    await engine.dispose()


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
logfire.instrument_fastapi(app=app, capture_headers=True)
logfire.instrument_sqlalchemy(angine=engine, enable_commenter=True)


# Register profiling middleware if enabled
register_profiling_middleware(app, enabled=config.PROFILING_ENABLED)
app.include_router(pipeline_router)
app.include_router(pipeline_type_router)
app.include_router(pipeline_execution_router)
app.include_router(address_type_router)
app.include_router(address_router)
app.include_router(address_lineage_router)
app.include_router(timeliness_router)
app.include_router(anomaly_detection_router)
app.include_router(log_cleanup_router)
app.include_router(freshness_router)
app.include_router(celery_router)
app.include_router(diagnostics_router)


@app.get("/")
async def heartbeat():
    return {"status": "ok"}


@app.get("/scalar", include_in_schema=False)
async def get_scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Scalar API")
