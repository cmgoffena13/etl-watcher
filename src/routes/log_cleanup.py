from fastapi import APIRouter

from src.database.log_cleanup_utils import db_log_cleanup
from src.database.session import SessionDep
from src.models.log_cleanup import LogCleanupPostInput, LogCleanupPostOutput

router = APIRouter()


@router.post("/log_cleanup", response_model=LogCleanupPostOutput)
async def log_cleanup(session: SessionDep, config: LogCleanupPostInput):
    return await db_log_cleanup(session=session, config=config)
