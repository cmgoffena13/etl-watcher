Deployment Guide
=================

This section covers deployment strategies for Watcher.
   
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
~~~~~~~~~~

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
~~~~~~~

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

Deployment
~~~~~~~~~~

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

Service
~~~~~~~~~~

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

Ingress
~~~~~~~~~~

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

Database Setup
---------------

PostgreSQL Configuration
~~~~~~~~~~~~~~~~~~~~~~~

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


Post-Deployment
~~~~~~~~~~~~~~~

**Verification**

.. code-block:: bash

   # Check application health
   curl http://localhost:8000
   
   # Check database connectivity
   psql $DATABASE_URL -c "SELECT 1;"
   
   # Check Redis connectivity
   redis-cli -u $REDIS_URL ping

Rollback Strategy
~~~~~~~~~~~~~~~~

**Database Rollback**

.. code-block:: bash

   # Rollback migrations
   alembic downgrade -1
   
   # Verify rollback
   alembic current
   
   # Check application
   curl http://localhost:8000

**Data Rollback**

.. code-block:: bash

   # Restore from backup
   psql $DATABASE_URL < backup.sql
   
   # Verify data
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline;"

Monitoring & Alerting
---------------------

Health Checks
~~~~~~~~~~~~~~

**Application Health**

.. code-block:: bash

   # Health check endpoint
   curl http://localhost:8000
   
   # Diagnostics page
   curl http://localhost:8000/diagnostics

**Redis Health**

.. code-block:: bash

   # Redis connectivity
   redis-cli -u $REDIS_URL ping
   
   # Redis performance
   redis-cli -u $REDIS_URL --latency
   
   # Redis memory
   redis-cli -u $REDIS_URL info memory

Alerting Setup
~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~

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

   # Default connection pool settings
   pool_size = 20
   max_overflow = 10
   pool_timeout = 30
   pool_recycle = 3600

Redis Optimization
~~~~~~~~~~~~~~~~~~

**Performance Monitoring**

.. code-block:: bash

   # Monitor Redis performance
   redis-cli --latency
   
   # Check memory usage
   redis-cli info memory
   
   # Monitor operations
   redis-cli monitor

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

Recovery Procedures
~~~~~~~~~~~~~~~~~~~

**Database Recovery**

.. code-block:: bash

   # Restore database
   psql $DATABASE_URL < backup.sql
   
   # Verify data
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline;"
   
   # Run migrations
   alembic upgrade head