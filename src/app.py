import logging
from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pyinstrument import Profiler
from pyinstrument.renderers.html import HTMLRenderer
from rich import panel, print
from scalar_fastapi import get_scalar_api_reference

from src.database.db import create_initial_records, create_test_db, reset_database
from src.database.session import engine, test_connection
from src.logging_conf import configure_logging
from src.middleware import register_profiling_middleware
from src.responses import ORJSONResponse
from src.routes import (
    address_lineage_router,
    address_router,
    address_type_router,
    anomaly_detection_router,
    freshness_router,
    log_cleanup_router,
    pipeline_execution_router,
    pipeline_router,
    pipeline_type_router,
    timeliness_router,
)
from src.settings import config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(panel.Panel("Server is starting up...", border_style="green"))
    configure_logging()
    await test_connection()
    # await create_test_db()
    # await reset_database()
    # await create_initial_records()
    yield
    print(panel.Panel("Server is shutting down...", border_style="red"))
    # Close the connection pool
    await engine.dispose()


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
logfire.instrument_fastapi(app=app, capture_headers=True)
logfire.instrument_sqlalchemy(angine=engine, enable_commenter=True)

# Register profiling middleware
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


@app.get("/")
async def heartbeat():
    return {"status": "ok"}


@app.get("/scalar", include_in_schema=False)
async def get_scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Scalar API")
