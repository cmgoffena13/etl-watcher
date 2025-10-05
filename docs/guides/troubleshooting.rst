Troubleshooting
===============

This guide helps you diagnose and resolve common issues with Watcher.

Common Issues
-------------

Installation Issues
~~~~~~~~~~~~~~~~~~~

**Port Already in Use**
   **Problem**: Ports 8000, 5432, or 6379 are already in use
   
   **Solution**:

   
   .. code-block:: bash

      # Check what's using the ports
      lsof -i :8000
      lsof -i :5432
      lsof -i :6379
      
      # Kill processes if needed
      kill -9 <PID>
      
      # Or use different ports
      docker-compose -f docker-compose.yml up -d --scale app=0
      docker-compose -f docker-compose.yml up -d -p 8001:8000

**Database Connection Failed**
   **Problem**: Cannot connect to PostgreSQL
   
   **Solution**:

   
   .. code-block:: bash

      # Check if PostgreSQL is running
      docker ps | grep postgres
      
      # Check connection string
      echo $DATABASE_URL
      
      # Test connection
      psql $DATABASE_URL -c "SELECT 1;"
      
      # Restart PostgreSQL if needed
      docker-compose restart postgres

**Redis Connection Failed**
   **Problem**: Cannot connect to Redis
   
   **Solution**:

   
   .. code-block:: bash

      # Check if Redis is running
      docker ps | grep redis
      
      # Test Redis connection
      redis-cli -u $REDIS_URL ping
      
      # Restart Redis if needed
      docker-compose restart redis

**Migration Errors**
   **Problem**: Database migrations fail
   
   **Solution**:

   .. code-block:: bash

      # Check database exists
      psql $DATABASE_URL -c "SELECT 1;"
      
      # Check migration status
      alembic current
      
      # Run migrations
      alembic upgrade head
      
      # Check for conflicts
      alembic heads

Application Issues
------------------

**Application Won't Start**
   **Problem**: FastAPI application fails to start
   
   **Solution**:

   .. code-block:: bash

      # Check logs
      docker-compose logs app
      
      # Check environment variables
      docker-compose exec app env | grep -E "(DATABASE|REDIS|LOGFIRE)"
      
      # Check dependencies
      uv run python -c "import src.app"
      
      # Restart application
      docker-compose restart app

**Import Errors**
   **Problem**: Module import errors
   
   **Solution**:

   .. code-block:: bash

      # Check Python path
      uv run python -c "import sys; print(sys.path)"
      
      # Reinstall dependencies
      uv sync
      
      # Check for circular imports
      uv run python -c "import src.app"

**Configuration Errors**
   **Problem**: Configuration validation errors
   
   **Solution**:

   .. code-block:: bash

      # Check environment variables
      env | grep -E "(DEV|PROD|TEST)"
      
      # Validate configuration
      uv run python -c "from src.settings import config; print(config)"
      
      # Check .env file
      cat .env

Database Issues
---------------

**Connection Timeouts**
   **Problem**: Database connection timeouts
   
   **Solution**:

   .. code-block:: bash

      # Check connection pool settings
      grep -r "pool_size" src/
      
      # Check database performance
      psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity;"
      
      # Restart database
      docker-compose restart postgres

**Query Performance**
   **Problem**: Slow database queries
   
   **Solution**:

   .. code-block:: bash

      # Check slow queries
      psql $DATABASE_URL -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
      
      # Check indexes
      psql $DATABASE_URL -c "SELECT schemaname, tablename, indexname FROM pg_indexes;"
      
      # Analyze tables
      psql $DATABASE_URL -c "ANALYZE;"

**Schema Issues**
   **Problem**: Database schema problems
   
   **Solution**:

   .. code-block:: bash

      # Check schema
      psql $DATABASE_URL -c "\d"
      
      # Check migrations
      alembic current
      alembic history
      
      # Reset schema if needed
      alembic downgrade base
      alembic upgrade head

Celery Issues
-------------

**Workers Not Starting**
   **Problem**: Celery workers fail to start
   
   **Solution**:

   .. code-block:: bash

      # Check worker logs
      docker-compose logs celery
      
      # Check Redis connection
      redis-cli -u $REDIS_URL ping
      
      # Start worker manually
      celery -A src.celery_app worker --loglevel=info
      
      # Check worker status
      celery -A src.celery_app inspect active

**Tasks Not Processing**
   **Problem**: Tasks stuck in queue
   
   **Solution**:

   .. code-block:: bash

      # Check queue depth
      redis-cli -u $REDIS_URL llen celery
      
      # Check worker status
      celery -A src.celery_app inspect active
      
      # Purge queue if needed
      celery -A src.celery_app purge
      
      # Restart workers
      docker-compose restart celery

**Task Failures**
   **Problem**: Tasks failing repeatedly
   
   **Solution**:

   .. code-block:: bash

      # Check task results
      celery -A src.celery_app inspect stats
      
      # Check error logs
      docker-compose logs celery | grep ERROR
      
      # Test task manually
      celery -A src.celery_app call src.celery_tasks.freshness_check_task

**Queue Backlog**
   **Problem**: Queue building up with tasks
   
   **Solution**:

   .. code-block:: bash

      # Check queue depth
      redis-cli -u $REDIS_URL llen celery
      
      # Scale workers
      docker-compose up -d --scale celery=3
      
      # Check worker performance
      celery -A src.celery_app inspect stats

Monitoring Issues
-----------------

**Freshness Checks Failing**
   **Problem**: Freshness monitoring not working
   
   **Solution**:

   .. code-block:: bash

      # Check freshness task
      curl -X POST "http://localhost:8000/freshness"
      
      # Check task queue
      redis-cli -u $REDIS_URL llen celery
      
      # Check worker logs
      docker-compose logs celery | grep freshness
      
      # Test manually
      celery -A src.celery_app call src.celery_tasks.freshness_check_task

**Timeliness Checks Failing**
   **Problem**: Timeliness monitoring not working
   
   **Solution**:

   .. code-block:: bash

      # Check timeliness task
      curl -X POST "http://localhost:8000/timeliness" -H "Content-Type: application/json" -d '{"lookback_minutes": 60}'
      
      # Check task queue
      redis-cli -u $REDIS_URL llen celery
      
      # Check worker logs
      docker-compose logs celery | grep timeliness
      
      # Test manually
      celery -A src.celery_app call src.celery_tasks.timeliness_check_task

**Anomaly Detection Not Working**
   **Problem**: Anomaly detection not running
   
   **Solution**:

   .. code-block:: bash

      # Check anomaly detection rules
      curl -X GET "http://localhost:8000/anomaly_detection_rule"
      
      # Check pipeline executions
      curl -X GET "http://localhost:8000/pipeline"
      
      # Check task queue
      redis-cli -u $REDIS_URL llen celery
      
      # Test manually
      celery -A src.celery_app call src.celery_tasks.detect_anomalies_task --args='[1, 123]'

**Alerts Not Sending**
   **Problem**: Slack alerts not being sent
   
   **Solution**:

   .. code-block:: bash

      # Check Slack webhook
      echo $SLACK_WEBHOOK_URL
      
      # Test webhook
      curl -X POST $SLACK_WEBHOOK_URL -H "Content-Type: application/json" -d '{"text": "Test message"}'
      
      # Check alert logs
      docker-compose logs app | grep -i slack
      
      # Check environment variables
      docker-compose exec app env | grep SLACK

Performance Issues
------------------

**Slow API Responses**
   **Problem**: API endpoints responding slowly
   
   **Solution**:

   .. code-block:: bash

      # Check database performance
      psql $DATABASE_URL -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"
      
      # Check connection pool
      grep -r "pool_size" src/
      
      # Check Redis performance
      redis-cli -u $REDIS_URL --latency
      
      # Monitor system resources
      docker stats

**High Memory Usage**
   **Problem**: Application using too much memory
   
   **Solution**:

   .. code-block:: bash

      # Check memory usage
      docker stats
      
      # Check for memory leaks
      docker-compose logs app | grep -i memory
      
      # Restart application
      docker-compose restart app
      
      # Check worker memory
      docker-compose logs celery | grep -i memory

**Database Performance**
   **Problem**: Database queries running slowly
   
   **Solution**:

   .. code-block:: bash

      # Check slow queries
      psql $DATABASE_URL -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
      
      # Check indexes
      psql $DATABASE_URL -c "SELECT schemaname, tablename, indexname FROM pg_indexes WHERE tablename LIKE '%pipeline%';"
      
      # Analyze tables
      psql $DATABASE_URL -c "ANALYZE;"
      
      # Check database size
      psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size(current_database()));"

**Redis Performance**
   **Problem**: Redis operations running slowly
   
   **Solution**:

   .. code-block:: bash

      # Check Redis performance
      redis-cli -u $REDIS_URL --latency
      
      # Check Redis memory
      redis-cli -u $REDIS_URL info memory
      
      # Check Redis keys
      redis-cli -u $REDIS_URL keys "*" | wc -l
      
      # Clear Redis if needed
      redis-cli -u $REDIS_URL flushdb

Debugging Techniques
--------------------

**Enable Debug Logging**
   **Solution**:

   .. code-block:: bash

      # Set debug logging
      export LOG_LEVEL=DEBUG
      
      # Restart application
      docker-compose restart app
      
      # Check logs
      docker-compose logs -f app

**Database Debugging**
   **Solution**:

   .. code-block:: bash

      # Enable query logging
      export DATABASE_ECHO=true
      
      # Check database logs
      docker-compose logs postgres
      
      # Test queries manually
      psql $DATABASE_URL -c "SELECT * FROM pipeline LIMIT 5;"

**Celery Debugging**
   **Solution**:

   .. code-block:: bash

      # Enable Celery debug logging
      celery -A src.celery_app worker --loglevel=debug
      
      # Check task results
      celery -A src.celery_app inspect stats
      
      # Test tasks manually
      celery -A src.celery_app call src.celery_tasks.freshness_check_task

**API Debugging**
   **Solution**:

   .. code-block:: bash

      # Test API endpoints
      curl -v http://localhost:8000
      
      # Check API documentation
      curl http://localhost:8000/scalar
      
      # Test specific endpoints
      curl -X GET "http://localhost:8000/pipeline"

**Network Debugging**
   **Solution**:

   .. code-block:: bash

      # Check network connectivity
      docker-compose exec app ping postgres
      docker-compose exec app ping redis
      
      # Check port accessibility
      telnet localhost 8000
      telnet localhost 5432
      telnet localhost 6379

**Container Debugging**
   **Solution**:

   .. code-block:: bash

      # Check container status
      docker-compose ps
      
      # Check container logs
      docker-compose logs app
      docker-compose logs postgres
      docker-compose logs redis
      docker-compose logs celery
      
      # Execute commands in containers
      docker-compose exec app bash
      docker-compose exec postgres psql -U user -d watcher_dev

**Environment Debugging**
   **Solution**:

   .. code-block:: bash

      # Check environment variables
      docker-compose exec app env
      
      # Check configuration
      docker-compose exec app python -c "from src.settings import config; print(config)"
      
      # Check dependencies
      docker-compose exec app uv run python -c "import src.app"

**Database Debugging**
   **Solution**:

   .. code-block:: bash

      # Check database connection
      docker-compose exec app python -c "from src.database.session import engine; print(engine)"
      
      # Check migrations
      docker-compose exec app alembic current
      
      # Check database schema
      docker-compose exec postgres psql -U user -d watcher_dev -c "\d"

**Redis Debugging**
   **Solution**:

   .. code-block:: bash

      # Check Redis connection
      docker-compose exec app python -c "import redis; r = redis.from_url('redis://redis:6379/1'); print(r.ping())"
      
      # Check Redis keys
      docker-compose exec redis redis-cli keys "*"
      
      # Check Redis memory
      docker-compose exec redis redis-cli info memory

**Celery Debugging**
   **Solution**:

   .. code-block:: bash

      # Check Celery connection
      docker-compose exec app python -c "from src.celery_app import celery; print(celery.control.inspect().active())"
      
      # Check task queue
      docker-compose exec redis redis-cli llen celery
      
      # Check worker status
      docker-compose exec app celery -A src.celery_app inspect active

**API Debugging**
   **Solution**:

   .. code-block:: bash

      # Check API health
      curl -v http://localhost:8000
      
      # Check API documentation
      curl http://localhost:8000/scalar
      
      # Test specific endpoints
      curl -X GET "http://localhost:8000/pipeline"
      curl -X POST "http://localhost:8000/freshness"
      curl -X POST "http://localhost:8000/timeliness" -H "Content-Type: application/json" -d '{"lookback_minutes": 60}'

**Monitoring Debugging**
   **Solution**:

   .. code-block:: bash

      # Check diagnostics
      curl http://localhost:8000/diagnostics
      
      # Check monitoring endpoints
      curl -X POST "http://localhost:8000/freshness"
      curl -X POST "http://localhost:8000/timeliness" -H "Content-Type: application/json" -d '{"lookback_minutes": 60}'
      curl -X POST "http://localhost:8000/celery/monitor-queue"
      
      # Check monitoring logs
      docker-compose logs app | grep -i "freshness\|timeliness\|anomaly"

**Alerting Debugging**
   **Solution**:

   .. code-block:: bash

      # Check Slack webhook
      curl -X POST $SLACK_WEBHOOK_URL -H "Content-Type: application/json" -d '{"text": "Test message"}'
      
      # Check alert logs
      docker-compose logs app | grep -i slack
      
      # Check environment variables
      docker-compose exec app env | grep SLACK

**Performance Debugging**
   **Solution**:

   .. code-block:: bash

      # Check system resources
      docker stats
      
      # Check database performance
      psql $DATABASE_URL -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"
      
      # Check Redis performance
      redis-cli -u $REDIS_URL --latency
      
      # Check application performance
      curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000

**Load Testing Debugging**
   **Solution**:

   .. code-block:: bash

      # Run load tests
      locust -f src/diagnostics/locustfile.py --host=http://localhost:8000
      
      # Check load test results
      curl http://localhost:8089
      
      # Check system performance under load
      docker stats

**Security Debugging**
   **Solution**:

   .. code-block:: bash

      # Check SSL certificates
      openssl s_client -connect localhost:8000
      
      # Check authentication
      curl -v http://localhost:8000
      
      # Check authorization
      curl -X GET "http://localhost:8000/pipeline"

**Backup and Recovery**
   **Solution**:

   .. code-block:: bash

      # Backup database
      pg_dump $DATABASE_URL > backup.sql
      
      # Backup Redis
      redis-cli -u $REDIS_URL --rdb backup.rdb
      
      # Restore database
      psql $DATABASE_URL < backup.sql
      
      # Restore Redis
      redis-cli -u $REDIS_URL --pipe < backup.rdb

**Disaster Recovery**
   **Solution**:

   .. code-block:: bash

      # Check system status
      docker-compose ps
      
      # Restart all services
      docker-compose restart
      
      # Check logs
      docker-compose logs
      
      # Verify functionality
      curl http://localhost:8000
