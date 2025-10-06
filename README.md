# Watcher
**Open Source Metadata Framework for Data Engineers**

A comprehensive FastAPI-based metadata management system designed to monitor data pipeline executions, store watermarks, track data lineage, ensure timeliness & freshness of data, detect anomalies among operations, manage data addresses, and provide observability across your data infrastructure.

![Watcher](docs/_static/images/watcher.jpg)

![linesofcode](https://aschey.tech/tokei/github/cmgoffena13/watcher?category=code)

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

*See [Timeliness & Freshness](#-timeliness--freshness) section for detailed configuration and usage.*

### 🔗 Data Lineage Tracking
- **Address Management**: Track source and target data addresses with type classification
- **Lineage Relationships**: Create and maintain data flow relationships between sources and targets
- **Closure Table Pattern**: Efficient querying of complex lineage hierarchies with depth tracking
- **Source Control Integration**: Store lineage definitions in version control for reproducibility

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
- **Batched Processing**: Collect all anomalies for an execution and send a single comprehensive alert
- **Per-Metric Tracking**: Track anomaly status per metric using JSONB flags on pipeline executions
- **Auto-Create Rules**: Automatically create default anomaly detection rules for new pipelines

### 🧹 Log Cleanup
- **Automated Maintenance**: Remove old log data to maintain database performance
- **Batch Processing**: Safe deletion in configurable batches to avoid database locks
- **Cascading Cleanup**: Maintains referential integrity across related tables
- **Configurable Retention**: Set custom retention periods for different data types

### 🔧 Development & Operations
- **RESTful API**: Complete REST API for all operations with automatic documentation
- **Database Migrations**: Alembic-based migration system for schema evolution
- **Testing Framework**: Comprehensive test suite with fixtures and async support
- **Docker Support**: Containerized deployment with Docker
- **Logging & Observability**: Structured logging with Logfire integration

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation and settings management using Python type annotations
- **SQLModel** - SQL databases in Python, designed for simplicity and compatibility
- **PostgreSQL** - Robust relational database with JSONB support
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

## 🛠️ Development

### Development Setup
1. Install `uv`
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
2. Install python 3.12
```bash
uv python install 3.12
```
3. Check installation
```bash
uv python list
```
4. Sync python packages
```bash
uv sync --frozen --compile-bytecode
```
5. Add in pre-commits (you might need to run `source .venv/bin/activate` if your uv environment is not being recognized)
```bash
pre-commit install --install-hooks
```
6. Add in Environment Variables referencing `.env.example`

### Quick Start
```bash
# Start the development server
make dev-compose

# Run tests
make test

# Format and lint code
make format
```

### Database Management
```bash
# Add a new migration
make add-migration msg="description of changes"

# Apply migrations
make trigger-migration
```

### Performance Profiling

Watcher includes built-in performance profiling for development using pyinstrument to help identify bottlenecks and optimize your pipeline operations.

#### On-Demand Profiling

Profile any API endpoint by adding `?profile=true` to the URL:

#### Using Scalar API Docs

1. **Start your app**: `make dev-compose`
2. **Open Scalar**: http://localhost:8000/scalar
3. **Add `?profile=true`** as a query parameter to any endpoint URL in the interface
4. **Execute the request** - you'll get an interactive HTML profile directly in your browser

#### Profile Features

- **Interactive Call Stack**: Click to expand/collapse function calls
- **Timing Breakdown**: See exactly where time is spent
- **Database Operations**: Identify slow queries and connection issues
- **Memory Usage**: Track memory allocation patterns
- **Search & Filter**: Find specific functions or modules

#### Configuration

Profiling is enabled by default in development mode. To disable:

```bash
# Set in your environment
DEV_PROFILING_ENABLED=false
```

### Development Workflow
1. **Adding New Tables**: Add model to `src.database.models.__init__.py` for SQLModel metadata
2. **Database Migrations**: Use `make add-migration` to generate migration scripts
3. **Testing**: Use `make test` to run the comprehensive test suite
4. **Code Quality**: Pre-commit hooks automatically format and lint code