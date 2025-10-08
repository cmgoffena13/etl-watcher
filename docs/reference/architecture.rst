Architecture & Design
===============

Watcher is an Open Source ETL Metadata Framework designed for high-performance 
data pipeline monitoring and observability. 
Built with FastAPI and optimized for speed, it provides fast response times to ensure 
minimal impact on your data pipelines.

Design Philosophy
~~~~~~~~~~~~~~~~~

Watcher is built on several core design principles 
that guide its architecture and implementation:

Configuration as Code
--------------------

Watcher is designed to reflect configuration stored in source control. Any updates to the configuration in source control will be automatically reflected in Watcher through hash-based change detection. This ensures that the Watcher configuration stays synchronized with the configuration in your code.

**Key Benefits:**

- **Version Control Integration** - Pipeline and lineage definitions stored alongside ETL code
- **Automatic Synchronization** - Changes in code automatically update Watcher configuration
- **Reproducibility** - Same configuration across all environments
- **Code Review** - Pipeline changes go through the same review process as code changes

**Recommended Practice:**
Store your Pipeline configuration and Address Lineage in source control within your pipeline code for optimal integration.

Efficiency & Performance
------------------------

Watcher is designed to be efficient and performant to have minimal impact on the data pipelines it is monitoring. Any non-essential operations are designed to run in the background.

**Performance Features:**

- **Async Operations** - Non-blocking I/O for maximum throughput
- **Background Processing** - Heavy operations don't impact API response times
- **Connection Pooling** - Efficient database connection management
- **Optimized Queries** - Minimal database round trips with strategic indexing

Scalability
-----------

Watcher is designed to be scalable and handle large amounts of data. It can handle thousands of pipelines and millions of executions through a single instance.

**Scalability Features:**

- **Horizontal Scaling** - Multiple Celery workers for background processing
- **Database Optimization** - Efficient queries and indexing for large datasets
- **Resource Management** - Optimized memory and CPU usage
- **Load Distribution** - Celery task distribution across multiple workers

Reliability
-----------

Watcher is designed to be deployed on Kubernetes to allow for replicas and failover, ensuring high availability and fault tolerance.

**Reliability Features:**

- **Container Orchestration** - Kubernetes deployment for high availability
- **Task Persistence** - Redis-backed queues prevent task loss
- **Error Recovery** - Automatic retry logic with exponential backoff
- **Health Monitoring** - Comprehensive health checks and alerting

Observability
-------------

Watcher is designed to be observable through its integration with Logfire. Having an outside service monitoring the Watcher framework is essential for active monitoring.

**Observability Features:**

- **Centralized Logging** - Aggregated logs from all components
- **Performance Metrics** - Request/response time monitoring
- **Error Tracking** - Automatic error detection and alerting
- **Debugging Support** - Detailed request tracing and analysis

High-Level Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Watcher is built on a modern, high-performance stack designed for scalability and reliability:

**Core Components:**

- **FastAPI** - High-performance web framework with async support
- **PostgreSQL** - Reliable, open-source database with advanced features
- **Celery** - Distributed task queue for background processing
- **Redis** - Message broker and caching layer
- **Docker** - Containerization for deployment and scaling

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
- **Custom Enums** - Type-safe enumeration support for data validation
- **JSONB Support** - Flexible metadata storage with efficient querying

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

Docker Containerization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docker provides standardized deployment and development environments:

**Container Strategy:**

- **FastAPI Application** - Web API container with Gunicorn workers
- **Celery Workers** - Background task processing containers
- **Development Environment** - Docker Compose for local development
- **Production Deployment** - Kubernetes-ready container images

Logfire Integration
~~~~~~~~~~~~~~~~~~~

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
The Watcher framework provides comprehensive metadata management 
and monitoring capabilities while maintaining negligible performance impact on 
your data pipelines. This ensures that adding observability doesn't slow down your 
data processing workflows.
