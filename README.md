# Watcher
**Open Source Metadata Framework for Data Engineers**

A comprehensive FastAPI-based metadata management system designed to monitor data pipeline executions, store watermarks, track data lineage, ensure timeliness & freshness of data, detect anomalies among operations, manage data addresses, and provide observability across your data infrastructure.

In simple terms: Keep track of what your pipelines are doing!

![Watcher](docs/_static/images/watcher.jpg)

![linesofcode](https://aschey.tech/tokei/github/cmgoffena13/watcher?category=code)

## Table of Contents

Currently developing out an [SDK](https://github.com/cmgoffena13/etl-watcher-sdk)

1. [QuickStart](#quickstart)
2. [Features](#features)
3. [Technology Stack](#️-technology-stack)
4. [Contributing](#contributing)

## QuickStart
Utilize the [SDK](https://github.com/cmgoffena13/etl-watcher-sdk) once the Watcher Framework is deployed.
```
uv add etl-watcher-sdk
```

### Store Pipeline Configuration, Watermark logic, and Address Lineage
```python
import pendulum
from watcher import Pipeline, PipelineConfig, AddressLineage, Address

MY_ETL_PIPELINE_CONFIG = PipelineConfig(
    pipeline=Pipeline(
        name="my-etl-pipeline",
        pipeline_type_name="extraction",
    ),
    address_lineage=AddressLineage(
        source_addresses=[
            Address(
                name="source_db.source_schema.source_table",
                address_type_name="postgres",
                address_type_group_name="database",
            )
        ],
        target_addresses=[
            Address(
                name="target_db.target_schema.target_table",
                address_type_name="snowflake",
                address_type_group_name="warehouse",
            )
        ],
    ),
    default_watermark=pendulum.date(2025, 1, 1).to_date_string(),  # First Watermark is None otherwise
    next_watermark=pendulum.now("UTC").date().to_date_string()
)
```

### Sync Configuration with Watcher Framework and increment watermarks
```python
from watcher import Watcher

watcher = Watcher("https://api.watcher.example.com")

synced_config = watcher.sync_pipeline_config(MY_ETL_PIPELINE_CONFIG)

print(f"Pipeline synced!")
```

### Track Pipeline Executions
```python
from watcher import WatcherContext, ETLResult

@watcher.track_pipeline_execution(
    pipeline_id=synced_config.pipeline.id, 
    active=synced_config.pipeline.active,
    watermark=synced_config.watermark,
    next_watermark=synced_config.next_watermark
)
def etl_pipeline(watcher_context: WatcherContext):
    print("Starting ETL pipeline")

    print(f"Watermark: {watcher_context.watermark}")
    print(f"Next Watermark: {watcher_context.next_watermark}")
    
    # Your ETL work here, skip if Pipeline Inactive
    
    return ETLResult(
        completed_successfully=True,
        inserts=100,
        total_rows=100,
        execution_metadata={"partition": "2025-01-01"},
    )

etl_pipeline()
```

## Features

### 🔄 Pipeline Execution Monitoring
- **Execution Tracking**: Start and end pipeline executions with detailed metadata to track performance
- **Performance Metrics**: Track duration, DML counts (inserts, updates, deletes), and total rows processed
- **Execution History**: Maintain complete audit trail of all pipeline runs
- **Status Management**: Monitor active/inactive pipeline states
- **Nested Executions**: Support for hierarchical pipeline execution tracking using parent_id

### ⏰ Timeliness & Freshness Checks
- **Pipeline Execution Timeliness**: Monitor if pipeline executions complete within expected timeframes
- **DML Freshness Monitoring**: Check if data manipulation operations (inserts, updates, deletes) are recent enough
- **Configurable Thresholds**: Set custom rules per pipeline type and individual pipelines
- **Mute Capability**: Skip checks for specific pipelines when needed

### 🔗 Data Lineage Tracking
- **Address Management**: Track source and target data addresses with type classification
- **Lineage Relationships**: Create and maintain data flow relationships between sources and targets
- **Closure Table Pattern**: Efficient querying of complex lineage hierarchies with depth tracking
- **Source Control Integration**: Store lineage definitions in version control for reproducibility
- **Interactive Lineage Graph**: Visually explore lineage through addresses (nodes) and pipelines (edges)

### 📝 Configuration as Code
- **Source Control Integration**: Store pipeline configuration and address lineage definitions in version control
- **Hash-Based Change Detection**: Automatically detect when pipeline configuration changes and update the framework
- **Code as Source of Truth**: Your pipeline code defines the configuration, not manual database entries
- **Reproducible Deployments**: Same configuration across all environments through version control
- **Code Review Integration**: Review pipeline changes alongside code changes in pull requests
- **Rollback Capability**: Easy reversion of problematic configuration changes through git history

### 💧 Watermark Management
- **Incremental Processing**: Support for watermark-based incremental data pipelines
- **Flexible Watermarking**: Use any identifier (IDs, timestamps, etc.) as watermarks
- **Automatic Updates**: Watermarks are automatically updated after successful pipeline execution

### 📊 Metadata Storage
- **Pipeline Configuration**: Store pipeline arguments and configuration as JSONB
- **Type Classification**: Organize pipelines by type for better management and control
- **Address Type System**: Categorize data sources and targets by type and group

### 🚨 Anomaly Detection
- **Statistical Analysis**: Analyze individual pipeline executions against historical baselines using standard deviation and z-score analysis
- **Configurable Metrics**: Monitor duration, row counts, and DML operations for individual pipelines
- **Automatic Detection**: Run anomaly detection automatically after each pipeline execution
- **Historical Baselines**: Calculate statistical baselines from historical execution data over configurable time windows
- **Anomaly Exclusion**: Previously flagged anomalies are excluded from future baseline calculations to prevent skewing
- **Auto-Create Rules**: Automatically create default anomaly detection rules for new pipelines

### 🧹 Log Cleanup
- **Automated Maintenance**: Remove old log data to maintain database performance
- **Batch Processing**: Safe deletion in configurable batches to avoid database locks
- **Configurable Retention**: Set a custom retention period

### 🔧 Development & Operations
- **RESTful API**: Complete REST API for all operations with automatic documentation
- **Database Migrations**: Alembic-based migration system for schema evolution
- **Testing Framework**: Comprehensive test suite with fixtures and async support
- **Docker Support**: Containerized deployment with Docker
- **Logging & Observability**: Structured logging with Logfire integration

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast async web framework for building APIs
- **Pydantic** - Data validation and settings management using Python type annotations
- **SQLModel** - SQL databases in Python, designed for simplicity and compatibility
- **Alembic** - Database migration tool for SQLAlchemy
- **AsyncPG** - Async PostgreSQL driver
- **HTTPX** - Async HTTP client for external API calls (Slack)
- **Pendulum** - Better dates and times for Python

### Development & Testing
- **Pytest** - Testing framework with async support
- **Ruff** - Fast Python linter and formatter
- **Pre-commit** - Git hooks for code quality
- **UV** - Fast Python package manager
- **Scalar** - Interactive API documentation

### Logging & Observability
- **Logfire** - Comprehensive structured logging and observability platform
  - **Application Logs**: FastAPI request/response logging with automatic instrumentation
  - **Database Logs**: SQLAlchemy query logging and performance monitoring
  - **Background Tasks**: Celery worker execution logging and task tracking
  - **Structured Data**: JSON-formatted logs with consistent metadata across all components
  - **Logical Grouping**: Logs organized by operation type (API, Database, Background Tasks)
  - **Performance Insights**: Automatic timing and performance metrics collection
  - **Error Tracking**: Detailed error context and stack traces with correlation IDs

### Infrastructure
- **Docker** - Containerization
- **Uvicorn** - ASGI server for FastAPI
- **Gunicorn** - WSGI server to handle mutliple Uvicorn workers
- **Celery** - Distributed task queue for background processing
- **Redis** - Message broker and result backend for Celery
- **Postgres** - Robust relational database with JSONB support

## Contributing

I welcome contributions to Watcher! Please see the [Contributing Guidelines](CONTRIBUTING.md) for details on how to get started, the development process, and how to submit pull requests.

### Quick Start for Contributors
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. You'll need a free postgres test database (I recommend using [SupaBase](https://supabase.com))
5. Run tests with `make test`
6. Submit a pull request

For detailed information about the coding standards, testing requirements, and contribution process, please refer to the [Contributing Guidelines](CONTRIBUTING.md).