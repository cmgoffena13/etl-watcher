Deployment Guide
=================

This section covers deployment strategies for Watcher.
   
Kubernetes
----------

Namespace
~~~~~~~~~

.. code-block:: yaml

   apiVersion: v1
   kind: Namespace
   metadata:
     name: watcher


ConfigMap
~~~~~~~~~

.. code-block:: yaml

   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: watcher-config
     namespace: watcher
   data:
     PROD_DATABASE_URL: "postgresql+asyncpg://user:password@your-db-host:5432/watcher"
     PROD_REDIS_URL: "redis://your-redis-host:6379/1"
     PROD_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES: "true"
     PROD_PROFILING_ENABLED: "false"

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
     PROD_LOGFIRE_TOKEN: <base64-encoded-token>
     PROD_SLACK_WEBHOOK_URL: <base64-encoded-webhook>

Watcher Application
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: watcher-app
     namespace: watcher
   spec:
     replicas: 2
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
           livenessProbe:
             httpGet:
               path: /
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5
           resources:
             requests:
               memory: "512Mi"
               cpu: "250m"
             limits:
               memory: "1Gi"
               cpu: "500m"

   ---
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
     type: ClusterIP

Celery Workers
~~~~~~~~~~~~~~

.. code-block:: yaml

   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: watcher-celery
     namespace: watcher
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: watcher-celery
     template:
       metadata:
         labels:
           app: watcher-celery
       spec:
         containers:
         - name: celery
           image: watcher:latest
           command: ["celery", "-A", "src.celery_app", "worker", "--loglevel=info"]
           envFrom:
           - configMapRef:
               name: watcher-config
           - secretRef:
               name: watcher-secrets
           resources:
             requests:
               memory: "256Mi"
               cpu: "100m"
             limits:
               memory: "512Mi"
               cpu: "250m"


Deployment Configuration
------------------------

PostgreSQL Configuration
~~~~~~~~~~~~~~~~~~~~~~~

**Connection Pooling**

.. code-block:: python

   # Default connection pool settings
   pool_size = 20
   max_overflow = 10
   pool_timeout = 30
   pool_recycle = 3600

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
   
   # Clean up logs daily (365 days retention)
   0 2 * * * curl -X POST http://localhost:8000/log_cleanup -H "Content-Type: application/json" -d '{"retention_days": 365}'

Deployment Strategy
-------------------

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

Health Checks
~~~~~~~~~~~~~~

**Application Health**

.. code-block:: bash

   # Health check endpoint
   curl http://localhost:8000

**Redis Health**

.. code-block:: bash

   # Redis connectivity
   redis-cli -u $REDIS_URL ping
   
   # Redis performance
   redis-cli -u $REDIS_URL --latency
   
   # Redis memory
   redis-cli -u $REDIS_URL info memory

Production Maintenance
----------------------

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

**Index Optimization**

.. code-block:: sql

   -- Analyze tables regularly
   ANALYZE;
   
   -- Update statistics
   UPDATE pg_stat_user_tables SET n_tup_ins = 0, n_tup_upd = 0, n_tup_del = 0;
   
   -- Vacuum tables
   VACUUM ANALYZE;

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

**Performance Tuning**

.. code-block:: bash

   # Check Redis performance
   redis-cli --latency
   
   # Monitor memory usage
   redis-cli info memory
   
   # Check key count
   redis-cli dbsize

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