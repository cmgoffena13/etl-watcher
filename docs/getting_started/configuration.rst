Configuration
=============

Environment Variables
---------------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Database
   DEV_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/watcher_dev
   
   # Redis
   DEV_REDIS_URL=redis://localhost:6379/1
   
   # Monitoring
   DEV_LOGFIRE_TOKEN=your_logfire_token_here
   DEV_LOGFIRE_CONSOLE=false
   
   # Notifications
   DEV_SLACK_WEBHOOK_URL=your_slack_webhook_url_here
   
   # Features
   DEV_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=false
   DEV_PROFILING_ENABLED=true

Production Environment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Database
   PROD_DATABASE_URL=postgresql+asyncpg://user:password@prod-db:5432/watcher_prod
   
   # Redis
   PROD_REDIS_URL=redis://prod-redis:6379/1
   
   # Monitoring
   PROD_LOGFIRE_TOKEN=your_production_logfire_token
   PROD_LOGFIRE_CONSOLE=false
   
   # Notifications
   PROD_SLACK_WEBHOOK_URL=your_production_slack_webhook
   
   # Features
   PROD_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=true
   PROD_PROFILING_ENABLED=false

Database Configuration
----------------------

Connection Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Host** Database server hostname
- **Port** Database port (default: 5432)
- **Database** Database name
- **Username** Database username
- **Password** Database password
- **SSL** SSL connection settings

Connection Pool Settings
~~~~~~~~~~~~~~~~~~~~~~~~

- **Pool Size** 20 connections
- **Max Overflow** 10 additional connections
- **Pool Timeout** 30 seconds
- **Pool Recycle** 3600 seconds

Redis Configuration
------------------

Connection Settings
~~~~~~~~~~~~~~~~~~~

- **Host** Redis server hostname
- **Port** Redis port (default: 6379)
- **Database** Redis database number (default: 1)
- **Password** Redis password (if required)

Celery Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Broker** Redis URL for message broker
- **Backend** Redis URL for result backend
- **Task Serializer** JSON
- **Result Serializer** JSON
- **Accept Content** JSON
- **Time Zone** UTC

Monitoring Configuration
------------------------

Logfire Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Logfire provides comprehensive observability for your Watcher instance:

- **Application Metrics** Request/response times, error rates
- **Database Queries** Query performance and slow query detection
- **Background Tasks** Celery worker execution logging and task tracking
- **Custom Events** Pipeline execution tracking and anomaly detection

Setup:

1. Create a Logfire account at https://logfire.pydantic.dev
2. Get your token from the Logfire dashboard
3. Set the ``LOGFIRE_TOKEN`` environment variable
4. Restart your application

Slack Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure Slack webhooks for real-time alerts:

1. Create a Slack app in your workspace
2. Add an Incoming Webhook to your app
3. Copy the webhook URL
4. Set the ``SLACK_WEBHOOK_URL`` environment variable

Alert Types:

- **Queue Monitoring** Celery queue depth alerts
- **Anomaly Detection** Statistical anomaly alerts
- **System Health** Database and Redis connectivity issues

Feature Flags
-------------

Auto-Create Anomaly Detection Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When enabled, Watcher automatically creates anomaly detection rules for new pipelines:

.. code-block:: bash

   WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=true

Profiling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable application profiling for performance analysis:

.. code-block:: bash

   PROFILING_ENABLED=true

Security Configuration
----------------------

Database Security
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Use strong passwords
- Enable SSL connections in production
- Restrict database access to application servers only
- Regular security updates

Redis Security
~~~~~~~~~~~~~~

- Use authentication if Redis is exposed
- Enable TLS in production
- Restrict network access
- Regular security updates

API Security
~~~~~~~~~~~~

- Use HTTPS in production
- Implement API rate limiting
- Validate all input data
- Regular security audits

Performance Tuning
-----------------

Database Optimization
~~~~~~~~~~~~~~~~~~~~

- **Indexes** Ensure proper indexing on frequently queried columns
- **Connection Pooling** Tune pool size based on load
- **Query Optimization** Monitor and optimize slow queries
- **Vacuum** Regular database maintenance

Redis Optimization
~~~~~~~~~~~~~~~~~~

- **Memory** Monitor Redis memory usage
- **Persistence** Configure appropriate persistence settings
- **Eviction** Set appropriate eviction policies
- **Monitoring** Monitor Redis performance metrics

Celery Optimization
~~~~~~~~~~~~~~~~~~~~

- **Workers** Scale workers based on task volume
- **Rate Limits** Configure appropriate rate limits
- **Retries** Tune retry policies
- **Monitoring** Monitor worker performance and queue depth
