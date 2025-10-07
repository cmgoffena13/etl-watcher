Configuration
=============

Environment Variables
---------------------

.. note::
   All environment variables must be prefixed with the environment name:
   
   - **Development**: ``DEV_`` prefix (e.g., ``DEV_DATABASE_URL``)
   - **Test**: ``TEST_`` prefix (e.g., ``TEST_DATABASE_URL``)
   - **Production**: ``PROD_`` prefix (e.g., ``PROD_DATABASE_URL``)

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash
   # Monitoring (optional)
   DEV_LOGFIRE_TOKEN=your_logfire_token_here
   DEV_LOGFIRE_CONSOLE=false
   
   # Notifications (optional)
   DEV_SLACK_WEBHOOK_URL=your_slack_webhook_url_here
   
   # Features
   DEV_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=false
   DEV_PROFILING_ENABLED=true

Production Environment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Database (Dev has Docker Compose)
   PROD_DATABASE_URL=postgresql+asyncpg://user:password@prod-db:5432/watcher_prod
   
   # Redis (Dev has Docker Compose)
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

Connection Pool Default Settings
~~~~~~~~~~~~~~~~~~~~~~~~

- **Pool Size** 20 connections
- **Max Overflow** 10 additional connections
- **Pool Timeout** 30 seconds
- **Pool Recycle** 3600 seconds

Redis Configuration
------------------

Connection Default Settings
~~~~~~~~~~~~~~~~~~~

- **Host** Redis server hostname
- **Port** Redis port (default: 6379)
- **Database** Redis database number (default: 1)

Celery Default Configuration
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

Setup:

1. Create a Logfire account at https://logfire.pydantic.dev (Free tier is 10 million calls per month)
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

- **Queue Monitoring**: Celery queue depth alerts
- **Anomaly Detection**: Statistical anomaly alerts
- **Timeliness**: Pipeline execution timeliness alerts
- **Freshness**: DML operation freshness alerts

Feature Flags
-------------

Auto-Create Anomaly Detection Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When enabled, Watcher automatically creates anomaly detection rules for new pipelines:

.. code-block:: bash

   WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=true

Profiling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable application profiling for performance analysis. Enabling this allows you to profile any API endpoint by adding `?profile=true` to the URL.

.. code-block:: bash

   PROFILING_ENABLED=true
