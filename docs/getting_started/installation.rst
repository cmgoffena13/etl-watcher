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
      DEV_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/watcher_dev
      DEV_REDIS_URL=redis://localhost:6379/1
      DEV_LOGFIRE_TOKEN=your_logfire_token_here
      DEV_SLACK_WEBHOOK_URL=your_slack_webhook_url_here

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

Required Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``DATABASE_URL`` - PostgreSQL connection string
- ``REDIS_URL`` - Redis connection string
- ``LOGFIRE_TOKEN`` - Logfire monitoring token (optional)

Optional Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``SLACK_WEBHOOK_URL`` - Slack notifications
- ``WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES`` - Auto-create rules (default: false)
- ``PROFILING_ENABLED`` - Enable profiling (default: false)
