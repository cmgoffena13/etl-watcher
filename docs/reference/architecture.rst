Architecture
===============

Watcher is an Open Source ETL Metadata Framework designed for high-performance data pipeline monitoring and observability. Built with FastAPI and optimized for speed, it provides fast response times to ensure minimal impact on your data pipelines.

High-Level Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Watcher is built on a modern, high-performance stack designed for scalability and reliability:

**Core Components:**

- **FastAPI** - High-performance web framework with async support
- **PostgreSQL** - Reliable, open-source database with advanced features
- **Celery** - Distributed task queue for background processing
- **Redis** - Message broker and caching layer
- **Docker** - Containerization for deployment and scaling

**Design Philosophy:**

- **High Performance** - Optimized for fast response times and minimal pipeline impact
- **Scalability** - Designed to handle large-scale data operations
- **Reliability** - Built with production-grade components and error handling
- **Observability** - Comprehensive monitoring and alerting capabilities

FastAPI Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FastAPI was chosen for its simplicity, speed, and modern async capabilities:

**Key Features:**

- **orjson Integration** - Fast JSON serialization/deserialization for optimal performance
- **Gunicorn + Uvicorn** - Production-ready ASGI server with worker management
- **asyncpg Integration** - Fastest asynchronous PostgreSQL driver
- **Connection Pooling** - Efficient database connection management
- **Pydantic Validation** - Automatic request/response validation with database constraint enforcement
- **Full Async Support** - Asynchronous operations throughout the application

**Performance Benefits:**

- Sub-second response times for all API endpoints
- Minimal overhead on pipeline execution
- High concurrency support for multiple simultaneous requests

PostgreSQL Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PostgreSQL provides the robust, scalable foundation for Watcher's metadata storage:

**Optimizations:**

- **RETURNING Clauses** - Combines INSERT/UPDATE and SELECT operations to minimize database trips
- **Strategic Indexing** - Comprehensive indexing strategy designed for large table growth
- **BIGINT Support** - Handles massive scale (beyond 2 billion records)
- **Check Constraints** - Data quality enforcement at the database level
- **JSONB Support** - Flexible metadata storage with efficient querying

**Database Features:**

- **Closure Tables** - Efficient hierarchical relationship queries for pipeline executions and address lineage
- **Custom Enums** - Type-safe enumeration support for data validation
- **Timezone Awareness** - Proper handling of temporal data across time zones
- **Foreign Key Constraints** - Referential integrity enforcement

Celery Background Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Celery handles time-consuming operations to keep the main API responsive:

**Performance Features:**

- **Rate Limiting** - Protects database from overwhelming requests
- **Task Duration Logging** - Performance monitoring and analysis
- **Scalable Workers** - Horizontal scaling for increased throughput
- **Retry Logic** - Automatic failure recovery with exponential backoff

Redis Message Broker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Redis serves as the message broker and provides additional functionality:

**Primary Functions:**

- **Celery Queue** - Task distribution and management
- **Persistence** - Queue durability for reliability
- **Task Duration Storage** - Performance metrics collection
- **Queue Monitoring** - Real-time queue status and health checks

**Benefits:**

- **High Performance** - Fast message passing and caching
- **Reliability** - Persistent queues prevent task loss
- **Monitoring** - Built-in queue health and performance metrics

Docker Containerization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docker provides standardized deployment and development environments:

**Container Strategy:**

- **FastAPI Application** - Web API container with Gunicorn workers
- **Celery Workers** - Background task processing containers
- **Development Environment** - Docker Compose for local development
- **Production Deployment** - Kubernetes-ready container images

Logfire Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Logfire provides comprehensive logging and monitoring capabilities:

**Features:**

- **Centralized Logging** - Aggregates logs from FastAPI and Celery workers
- **Error Rate Monitoring** - Automatic alerting for error rate spikes
- **Performance Tracking** - Request/response time monitoring
- **Debugging Support** - Detailed request tracing and error analysis

**Benefits:**

- **Observability** - Complete visibility into system behavior
- **Alerting** - Proactive issue detection and notification
- **Debugging** - Easy troubleshooting with detailed logs
- **Performance Analysis** - Identify bottlenecks and optimization opportunities

Performance Design Goals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Watcher was designed with one primary goal: **minimal impact on your data pipelines**.

**Key Principles:**

- **Fast Response Times** - Every API call optimized for speed
- **Efficient Database Queries** - Minimal database round trips
- **Background Processing** - Heavy operations don't block API responses
- **Resource Optimization** - Efficient memory and CPU usage
- **Scalable Architecture** - Grows with your data infrastructure

**Result:**
The Watcher framework provides comprehensive metadata management and monitoring capabilities while maintaining negligible performance impact on your data pipelines. This ensures that adding observability doesn't slow down your data processing workflows.
