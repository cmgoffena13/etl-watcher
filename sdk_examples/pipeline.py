import pendulum

# Utilizing etl-watcher-sdk
from watcher import Address, AddressLineage, Pipeline, PipelineConfig

POLYGON_OPEN_CLOSE_PIPELINE_CONFIG = PipelineConfig(
    pipeline=Pipeline(
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
    address_lineage=AddressLineage(
        source_addresses=[
            Address(
                name="https://api.polygon.io/v1/open-close/",
                address_type_name="polygon",
                address_type_group_name="api",
            )
        ],
        target_addresses=[
            Address(
                name="prod.polygon.open_close",
                address_type_name="postgres",
                address_type_group_name="database",
                address_metadata={
                    "external_dependencies": [
                        {"type": "looker_dashboard", "name": "Sales Dashboard"}
                    ]
                },
            )
        ],
    ),
    default_watermark=pendulum.date(2025, 10, 1).to_date_string(),
    next_watermark=pendulum.now().date().to_date_string(),
)
