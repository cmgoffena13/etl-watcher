Installation
============

Prerequisites
-------------

- Docker and Docker Compose
- Git

System Requirements
-------------------

- **Memory** Minimum 4GB RAM, 8GB recommended
- **Storage** 10GB free space for logs and data
- **Network** Port 8000 (FastAPI) - other services run in Docker

Installation Steps
------------------

1. **Clone the repository**

   .. code-block:: bash

      git clone https://github.com/cmgoffena13/watcher.git
      cd watcher

2. **Set up environment variables**

   Create a `.env` file:

   .. code-block:: bash

      # Development
      ENV_STATE=dev
      TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/watcher_test
      DEV_LOGFIRE_TOKEN=your_logfire_token_here
      DEV_SLACK_WEBHOOK_URL=your_slack_webhook_url_here

   .. note::
      ``TEST_DATABASE_URL`` is only needed for tests.

3. **Start services with Docker Compose**

   .. code-block:: bash

      docker-compose up -d

Verification
-----------

Once running, you can verify the local development installation:

- **API Documentation** http://localhost:8000/scalar
- **Health Check** http://localhost:8000/
- **Diagnostics** http://localhost:8000/diagnostics

Environment Variables
---------------------

Minimum Required Production Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``PROD_DATABASE_URL`` - PostgreSQL connection string
- ``PROD_REDIS_URL`` - Redis connection string

Optional Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``PROD_LOGFIRE_TOKEN`` - Logfire monitoring token
- ``PROD_SLACK_WEBHOOK_URL`` - Slack notifications for alerting
- ``PROD_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES`` - Auto-create rules (default: false)
- ``PROD_PROFILING_ENABLED`` - Enable profiling (default: false)
