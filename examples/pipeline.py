import pendulum
from utils import Pipeline

PIPELINE_CONFIG = {
    "pipeline": Pipeline(
        name="polygon_open_close",
        pipeline_type_name="extraction",
        timeliness_number=20,
        timeliness_datepart="minute",
        freshness_number=1,
        freshness_datepart="day",
        pipeline_metadata={
            "description": "Daily stock price extraction from Polygon API",
            "owner": "data-team",
        },
    ),
    "lineage": {
        "pipeline_id": None,  # Will be set later
        "source_addresses": [
            {
                "name": "https://api.polygon.io/v1/open-close/",
                "address_type_name": "polygon",
                "address_type_group_name": "api",
            }
        ],
        "target_addresses": [
            {
                "name": "prod.polygon.open_close",
                "address_type_name": "postgres",
                "address_type_group_name": "database",
            }
        ],
    },
    "default_watermark": pendulum.date(2025, 1, 1).to_date_string(),
    "watermark": None,  # Will be set later
}
