# Watcher
**Open Source Metadata Framework for Data Engineers**

A comprehensive FastAPI-based metadata management system designed to monitor data pipeline executions, store watermarks, track data lineage, ensure timeliness & freshness of data, detect anomalies among operations, manage data addresses, and provide observability across your data infrastructure.

![Watcher](docs/_static/images/watcher.jpg)

![linesofcode](https://aschey.tech/tokei/github/cmgoffena13/watcher?category=code)

## Table of Contents

1. [Features](#features)
2. [Technology Stack](#️-technology-stack)
3. [Contributing](#contributing)

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
4. You'll need a free postgres test database (I recommending using [SupaBase](https://supabase.com))
5. Run tests with `make test`
6. Submit a pull request

For detailed information about the coding standards, testing requirements, and contribution process, please refer to the [Contributing Guidelines](CONTRIBUTING.md).