import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import HTMLResponse
from pyinstrument import Profiler
from pyinstrument.renderers.html import HTMLRenderer
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ProfilingMiddleware(BaseHTTPMiddleware):
    """Middleware for on-demand request profiling using pyinstrument"""

    def __init__(self, app, enabled: bool = False):
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.enabled or not request.query_params.get("profile", False):
            return await call_next(request)

        try:
            with Profiler(interval=0.001, async_mode="enabled") as profiler:
                response = await call_next(request)

            # Return HTML profile directly in browser
            renderer = HTMLRenderer()
            profile_content = profiler.output(renderer=renderer)
            return HTMLResponse(content=profile_content, media_type="text/html")

        except Exception as e:
            logger.error(f"Profiling failed: {e}")
            return await call_next(request)


def register_profiling_middleware(app, enabled: bool = False):
    """Register profiling middleware if enabled"""
    if enabled:
        app.add_middleware(ProfilingMiddleware, enabled=enabled)
        logger.info(
            "Profiling middleware enabled - use ?profile=true to profile requests"
        )
