import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from rich import panel, print
from scalar_fastapi import get_scalar_api_reference

from src.database.db import create_initial_records, create_test_db, reset_database
from src.database.session import test_connection
from src.logging_conf import configure_logging
from src.responses import ORJSONResponse
from src.routes import (
    address_type_router,
    pipeline_execution_router,
    pipeline_router,
    pipeline_type_router,
)

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


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)


app.include_router(pipeline_router)
app.include_router(pipeline_type_router)
app.include_router(pipeline_execution_router)
app.include_router(address_type_router)


@app.get("/")
async def heartbeat():
    return {"message": "I'm up!"}


@app.get("/scalar", include_in_schema=False)
async def get_scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Scalar API")
