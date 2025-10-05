Deployment Guide
=================

This section covers deployment strategies for Watcher.

Deployment Options
------------------

Docker Compose
~~~~~~~~~~~~~~

Development Deployment
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start all services
   docker-compose up -d
   
   # Check status
   docker-compose ps
   
   # View logs
   docker-compose logs -f

Production Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Set environment variables
   export PROD_DATABASE_URL="postgresql+asyncpg://user:password@prod-db:5432/watcher_prod"
   export PROD_REDIS_URL="redis://prod-redis:6379/1"
   export PROD_LOGFIRE_TOKEN="your_production_token"
   export PROD_SLACK_WEBHOOK_URL="your_production_webhook"
   
   # Start services
   docker-compose -f docker-compose.prod.yml up -d

Kubernetes
~~~~~~~~~~

Namespace Setup
~~~~~~~~~~~~~~~

.. code-block:: yaml

   apiVersion: v1
   kind: Namespace
   metadata:
     name: watcher

ConfigMap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: watcher-config
     namespace: watcher
   data:
     DATABASE_URL: "postgresql+asyncpg://user:password@postgres:5432/watcher"
     REDIS_URL: "redis://redis:6379/1"

Secrets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   apiVersion: v1
   kind: Secret
   metadata:
     name: watcher-secrets
     namespace: watcher
   type: Opaque
   data:
     LOGFIRE_TOKEN: <base64-encoded-token>
     SLACK_WEBHOOK_URL: <base64-encoded-webhook>

**Deployment**
.. code-block:: yaml

   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: watcher-app
     namespace: watcher
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: watcher-app
     template:
       metadata:
         labels:
           app: watcher-app
       spec:
         containers:
         - name: watcher
           image: watcher:latest
           ports:
           - containerPort: 8000
           envFrom:
           - configMapRef:
               name: watcher-config
           - secretRef:
               name: watcher-secrets

**Service**
.. code-block:: yaml

   apiVersion: v1
   kind: Service
   metadata:
     name: watcher-service
     namespace: watcher
   spec:
     selector:
       app: watcher-app
     ports:
     - port: 80
       targetPort: 8000
     type: LoadBalancer

**Ingress**
.. code-block:: yaml

   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: watcher-ingress
     namespace: watcher
   spec:
     rules:
     - host: watcher.example.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: watcher-service
               port:
                 number: 80

Environment Configuration
-------------------------

Development
********************~

**Environment Variables**
.. code-block:: bash

   # Database
   export DEV_DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/watcher_dev"
   
   # Redis
   export DEV_REDIS_URL="redis://localhost:6379/1"
   
   # Monitoring
   export DEV_LOGFIRE_TOKEN="your_dev_token"
   export DEV_LOGFIRE_CONSOLE="true"
   
   # Notifications
   export DEV_SLACK_WEBHOOK_URL="your_dev_webhook"
   
   # Features
   export DEV_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES="false"
   export DEV_PROFILING_ENABLED="true"

**Docker Compose**
.. code-block:: yaml

   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=${DEV_DATABASE_URL}
         - REDIS_URL=${DEV_REDIS_URL}
         - LOGFIRE_TOKEN=${DEV_LOGFIRE_TOKEN}
         - SLACK_WEBHOOK_URL=${DEV_SLACK_WEBHOOK_URL}
       depends_on:
         - postgres
         - redis
     
     postgres:
       image: postgres:15
       environment:
         - POSTGRES_PASSWORD=password
         - POSTGRES_DB=watcher_dev
       ports:
         - "5432:5432"
     
     redis:
       image: redis:7
       ports:
         - "6379:6379"

Production
~~~~~~~~~~

**Environment Variables**
.. code-block:: bash

   # Database
   export PROD_DATABASE_URL="postgresql+asyncpg://user:password@prod-db:5432/watcher_prod"
   
   # Redis
   export PROD_REDIS_URL="redis://prod-redis:6379/1"
   
   # Monitoring
   export PROD_LOGFIRE_TOKEN="your_production_token"
   export PROD_LOGFIRE_CONSOLE="false"
   
   # Notifications
   export PROD_SLACK_WEBHOOK_URL="your_production_webhook"
   
   # Features
   export PROD_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES="true"
   export PROD_PROFILING_ENABLED="false"

**Production Docker Compose**
.. code-block:: yaml

   version: '3.8'
   services:
     app:
       image: watcher:latest
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=${PROD_DATABASE_URL}
         - REDIS_URL=${PROD_REDIS_URL}
         - LOGFIRE_TOKEN=${PROD_LOGFIRE_TOKEN}
         - SLACK_WEBHOOK_URL=${PROD_SLACK_WEBHOOK_URL}
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
     
     celery:
       image: watcher:latest
       command: celery -A src.celery_app worker --loglevel=info
       environment:
         - DATABASE_URL=${PROD_DATABASE_URL}
         - REDIS_URL=${PROD_REDIS_URL}
         - LOGFIRE_TOKEN=${PROD_LOGFIRE_TOKEN}
         - SLACK_WEBHOOK_URL=${PROD_SLACK_WEBHOOK_URL}
       restart: unless-stopped
       depends_on:
         - app

Database Setup
---------------

PostgreSQL Configuration
~~~~~~~~~~~~~~~~~~~~~~~

**Production Settings**
.. code-block:: sql

   -- Connection settings
   max_connections = 200
   shared_buffers = 256MB
   effective_cache_size = 1GB
   
   -- Performance settings
   random_page_cost = 1.1
   effective_io_concurrency = 200
   
   -- Logging settings
   log_statement = 'all'
   log_duration = on
   log_min_duration_statement = 1000

**Index Optimization**
.. code-block:: sql

   -- Analyze tables regularly
   ANALYZE;
   
   -- Update statistics
   UPDATE pg_stat_user_tables SET n_tup_ins = 0, n_tup_upd = 0, n_tup_del = 0;
   
   -- Vacuum tables
   VACUUM ANALYZE;

Redis Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Production Settings**
.. code-block:: conf

   # Memory settings
   maxmemory 512mb
   maxmemory-policy allkeys-lru
   
   # Persistence settings
   save 900 1
   save 300 10
   save 60 10000
   
   # Logging settings
   loglevel notice
   logfile /var/log/redis/redis.log

**Performance Tuning**
.. code-block:: bash

   # Check Redis performance
   redis-cli --latency
   
   # Monitor memory usage
   redis-cli info memory
   
   # Check key count
   redis-cli dbsize

Migration Strategy
------------------

Pre-Deployment
~~~~~~~~~~~~~~

**Database Backup**
.. code-block:: bash

   # Backup database
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # Verify backup
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline;"

**Migration Testing**
.. code-block:: bash

   # Test migrations
   alembic upgrade head --sql
   
   # Run migrations
   alembic upgrade head
   
   # Verify migration
   alembic current

**Application Testing**
.. code-block:: bash

   # Test application
   curl http://localhost:8000/health
   
   # Test API endpoints
   curl http://localhost:8000/pipeline
   
   # Test diagnostics
   curl http://localhost:8000/diagnostics

Post-Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Verification**
.. code-block:: bash

   # Check application health
   curl http://localhost:8000/health
   
   # Check database connectivity
   psql $DATABASE_URL -c "SELECT 1;"
   
   # Check Redis connectivity
   redis-cli -u $REDIS_URL ping

**Monitoring**
.. code-block:: bash

   # Check application logs
   docker-compose logs -f app
   
   # Check Celery logs
   docker-compose logs -f celery
   
   # Check system resources
   docker stats

Rollback Strategy
~~~~~~~~~~~~~~~~

**Application Rollback**
.. code-block:: bash

   # Rollback application
   docker-compose down
   docker-compose up -d --scale app=0
   docker-compose up -d

**Database Rollback**
.. code-block:: bash

   # Rollback migrations
   alembic downgrade -1
   
   # Verify rollback
   alembic current
   
   # Check application
   curl http://localhost:8000/health

**Data Rollback**
.. code-block:: bash

   # Restore from backup
   psql $DATABASE_URL < backup.sql
   
   # Verify data
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline;"

Monitoring & Alerting
---------------------

Health Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Application Health**
.. code-block:: bash

   # Health check endpoint
   curl http://localhost:8000/health
   
   # Diagnostics page
   curl http://localhost:8000/diagnostics
   
   # Performance metrics
   curl http://localhost:8000/diagnostics/performance

**Database Health**
.. code-block:: bash

   # Connection performance
   curl http://localhost:8000/diagnostics/connection-performance
   
   # Schema health
   curl http://localhost:8000/diagnostics/schema-health
   
   # Database queries
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline;"

**Redis Health**
.. code-block:: bash

   # Redis connectivity
   redis-cli -u $REDIS_URL ping
   
   # Redis performance
   redis-cli -u $REDIS_URL --latency
   
   # Redis memory
   redis-cli -u $REDIS_URL info memory

**Celery Health**
.. code-block:: bash

   # Celery diagnostics
   curl http://localhost:8000/diagnostics/celery
   
   # Queue monitoring
   curl -X POST http://localhost:8000/celery/monitor-queue
   
   # Worker status
   celery -A src.celery_app inspect active

Alerting Setup
~~~~~~~~~~~~~~

**Slack Integration**
.. code-block:: bash

   # Set Slack webhook
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
   
   # Test webhook
   curl -X POST $SLACK_WEBHOOK_URL -H "Content-Type: application/json" -d '{"text": "Test message"}'
   
   # Restart application
   docker-compose restart app

**Monitoring Checks**
.. code-block:: bash

   # Freshness monitoring
   curl -X POST http://localhost:8000/freshness
   
   # Timeliness monitoring
   curl -X POST http://localhost:8000/timeliness -H "Content-Type: application/json" -d '{"lookback_minutes": 60}'
   
   # Queue monitoring
   curl -X POST http://localhost:8000/celery/monitor-queue

**Scheduled Monitoring**
.. code-block:: bash

   # Add to crontab
   # Check freshness every hour
   0 * * * * curl -X POST http://localhost:8000/freshness
   
   # Check timeliness every 30 minutes
   */30 * * * * curl -X POST http://localhost:8000/timeliness -H "Content-Type: application/json" -d '{"lookback_minutes": 60}'
   
   # Monitor Celery queue every 5 minutes
   */5 * * * * curl -X POST http://localhost:8000/celery/monitor-queue
   
   # Clean up logs daily
   0 2 * * * curl -X POST http://localhost:8000/log_cleanup

Performance Optimization
------------------------

Database Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Query Optimization**
.. code-block:: sql

   -- Check slow queries
   SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
   
   -- Check index usage
   SELECT schemaname, tablename, indexname FROM pg_indexes;
   
   -- Analyze tables
   ANALYZE;

**Connection Pooling**
.. code-block:: python

   # Connection pool settings
   pool_size = 20
   max_overflow = 10
   pool_timeout = 30
   pool_recycle = 3600

**Index Optimization**
.. code-block:: sql

   -- Create covering indexes
   CREATE INDEX ix_pipeline_execution_pipeline_start_end ON pipeline_execution(pipeline_id, start_date, end_date) INCLUDE (completed_successfully, duration_seconds);
   
   -- Create partial indexes
   CREATE INDEX ix_pipeline_execution_completed_true ON pipeline_execution(pipeline_id, start_date) WHERE completed_successfully = true;

Redis Optimization
~~~~~~~~~~~~~~~~~~

**Memory Optimization**
.. code-block:: conf

   # Memory settings
   maxmemory 512mb
   maxmemory-policy allkeys-lru
   
   # Eviction settings
   maxmemory-samples 5

**Performance Monitoring**
.. code-block:: bash

   # Monitor Redis performance
   redis-cli --latency
   
   # Check memory usage
   redis-cli info memory
   
   # Monitor operations
   redis-cli monitor

Celery Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Worker Scaling**
.. code-block:: bash

   # Scale workers
   docker-compose up -d --scale celery=3
   
   # Check worker status
   celery -A src.celery_app inspect active
   
   # Monitor worker performance
   celery -A src.celery_app inspect stats

**Queue Optimization**
.. code-block:: bash

   # Monitor queue depth
   redis-cli -u $REDIS_URL llen celery
   
   # Check queue performance
   redis-cli -u $REDIS_URL --latency
   
   # Purge queue if needed
   celery -A src.celery_app purge

Security Considerations
-----------------------

Database Security
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Connection Security**
.. code-block:: bash

   # Use SSL connections
   export DATABASE_URL="postgresql+asyncpg://user:password@host:5432/db?sslmode=require"
   
   # Use connection pooling
   export DATABASE_POOL_SIZE=20
   export DATABASE_MAX_OVERFLOW=10

**Access Control**
.. code-block:: sql

   -- Create application user
   CREATE USER watcher_app WITH PASSWORD 'secure_password';
   
   -- Grant permissions
   GRANT CONNECT ON DATABASE watcher TO watcher_app;
   GRANT USAGE ON SCHEMA public TO watcher_app;
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO watcher_app;
   
   -- Grant sequence permissions
   GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO watcher_app;

Redis Security
~~~~~~~~~~~~~~

**Authentication**
.. code-block:: conf

   # Require authentication
   requirepass secure_password
   
   # Disable dangerous commands
   rename-command FLUSHDB ""
   rename-command FLUSHALL ""

**Network Security**
.. code-block:: conf

   # Bind to specific interface
   bind 127.0.0.1
   
   # Disable external access
   protected-mode yes

Application Security
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Environment Variables**
.. code-block:: bash

   # Use secure passwords
   export DATABASE_PASSWORD="secure_password"
   export REDIS_PASSWORD="secure_password"
   
   # Use environment-specific settings
   export ENV_STATE="production"
   export PROFILING_ENABLED="false"

**API Security**
.. code-block:: python

   # Use HTTPS in production
   if config.ENV_STATE == "production":
       app.add_middleware(HTTPSRedirectMiddleware)
   
   # Add rate limiting
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter

**Logging Security**
.. code-block:: python

   # Don't log sensitive data
   import logging
   logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
   
   # Use secure logging
   import logfire
   logfire.configure(level="INFO")

Disaster Recovery
-----------------

Backup Strategy
~~~~~~~~~~~~~~

**Database Backup**
.. code-block:: bash

   # Daily backup
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
   
   # Weekly backup
   pg_dump $DATABASE_URL | gzip > backup_$(date +%Y%m%d).sql.gz
   
   # Monthly backup
   pg_dump $DATABASE_URL | gzip > backup_$(date +%Y%m).sql.gz

**Redis Backup**
.. code-block:: bash

   # Redis backup
   redis-cli -u $REDIS_URL --rdb backup.rdb
   
   # Compress backup
   gzip backup.rdb

**Application Backup**
.. code-block:: bash

   # Backup application code
   tar -czf watcher_$(date +%Y%m%d).tar.gz src/
   
   # Backup configuration
   cp .env backup_env_$(date +%Y%m%d).env

Recovery Procedures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Database Recovery**
.. code-block:: bash

   # Restore database
   psql $DATABASE_URL < backup.sql
   
   # Verify data
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline;"
   
   # Run migrations
   alembic upgrade head

**Redis Recovery**
.. code-block:: bash

   # Restore Redis
   redis-cli -u $REDIS_URL --pipe < backup.rdb
   
   # Verify data
   redis-cli -u $REDIS_URL dbsize

**Application Recovery**
.. code-block:: bash

   # Restore application
   tar -xzf watcher_$(date +%Y%m%d).tar.gz
   
   # Restore configuration
   cp backup_env_$(date +%Y%m%d).env .env
   
   # Restart application
   docker-compose up -d

**Full Recovery**
.. code-block:: bash

   # Stop all services
   docker-compose down
   
   # Restore database
   psql $DATABASE_URL < backup.sql
   
   # Restore Redis
   redis-cli -u $REDIS_URL --pipe < backup.rdb
   
   # Start services
   docker-compose up -d
   
   # Verify recovery
   curl http://localhost:8000/health

Maintenance Procedures
----------------------

Regular Maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Daily Tasks**
.. code-block:: bash

   # Check application health
   curl http://localhost:8000/health
   
   # Check database performance
   psql $DATABASE_URL -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"
   
   # Check Redis performance
   redis-cli -u $REDIS_URL --latency
   
   # Check Celery queue
   redis-cli -u $REDIS_URL llen celery

**Weekly Tasks**
.. code-block:: bash

   # Analyze database
   psql $DATABASE_URL -c "ANALYZE;"
   
   # Vacuum database
   psql $DATABASE_URL -c "VACUUM;"
   
   # Check disk space
   df -h
   
   # Check memory usage
   free -h

**Monthly Tasks**
.. code-block:: bash

   # Full database backup
   pg_dump $DATABASE_URL | gzip > backup_$(date +%Y%m).sql.gz
   
   # Redis backup
   redis-cli -u $REDIS_URL --rdb backup_$(date +%Y%m).rdb
   
   # Log cleanup
   curl -X POST http://localhost:8000/log_cleanup
   
   # Performance review
   psql $DATABASE_URL -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

**Quarterly Tasks**
.. code-block:: bash

   # Security audit
   # Review access logs
   # Update dependencies
   # Performance optimization
   # Disaster recovery testing

Troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Common Issues**
.. code-block:: bash

   # Application won't start
   docker-compose logs app
   
   # Database connection issues
   psql $DATABASE_URL -c "SELECT 1;"
   
   # Redis connection issues
   redis-cli -u $REDIS_URL ping
   
   # Celery worker issues
   docker-compose logs celery

**Performance Issues**
.. code-block:: bash

   # Check system resources
   docker stats
   
   # Check database performance
   psql $DATABASE_URL -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"
   
   # Check Redis performance
   redis-cli -u $REDIS_URL --latency
   
   # Check Celery performance
   celery -A src.celery_app inspect stats

**Recovery Issues**
.. code-block:: bash

   # Check backup integrity
   pg_restore --list backup.sql
   
   # Test restore
   psql $DATABASE_URL < backup.sql
   
   # Verify data
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline;"
