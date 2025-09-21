from src.routes.address import router as address_router
from src.routes.address_lineage import router as address_lineage_router
from src.routes.address_type import router as address_type_router
from src.routes.anomaly_detection import router as anomaly_detection_router
from src.routes.celery import router as celery_router
from src.routes.diagnostics import router as diagnostics_router
from src.routes.freshness import router as freshness_router
from src.routes.log_cleanup import router as log_cleanup_router
from src.routes.pipeline import router as pipeline_router
from src.routes.pipeline_execution import router as pipeline_execution_router
from src.routes.pipeline_type import router as pipeline_type_router
from src.routes.reporting import router as reporting_router
from src.routes.timeliness import router as timeliness_router

__all__ = [
    "address_router",
    "address_lineage_router",
    "address_type_router",
    "anomaly_detection_router",
    "celery_router",
    "diagnostics_router",
    "freshness_router",
    "log_cleanup_router",
    "pipeline_router",
    "pipeline_execution_router",
    "pipeline_type_router",
    "timeliness_router",
    "reporting_router",
]
