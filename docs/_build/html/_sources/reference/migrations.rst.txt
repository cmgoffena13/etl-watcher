Database Migrations
====================

Watcher uses Alembic for database migration management for these features:

- **Version Control** Track schema changes over time
- **Rollback Support** Revert schema changes when needed
- **Data Preservation** Maintain data integrity during changes

Migration Files
---------------

Current Migrations
~~~~~~~~~~~~~~~~~~

**Initial Migration** (20251005124405_initial.py):

- Creates all core tables and relationships
- Establishes complete database schema for Watcher
- Sets up indexes, constraints, and foreign keys
- Creates custom PostgreSQL enums (DatePartEnum, AnomalyMetricFieldEnum)
- Establishes closure tables for hierarchical relationships
- Sets up anomaly detection and monitoring infrastructure

What the Initial Migration Establishes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The initial migration creates the complete Watcher database schema:

**Core Tables:**

- ``address_type`` - Address type definitions (database, table, etc.)
- ``pipeline_type`` - Pipeline type definitions with monitoring configuration
- ``address`` - Data source and target addresses
- ``pipeline`` - Pipeline definitions with lineage and monitoring settings
- ``pipeline_execution`` - Pipeline execution records with performance metrics
- ``address_lineage`` - Data lineage relationships between addresses
- ``anomaly_detection_rule`` - Anomaly detection configuration
- ``anomaly_detection_result`` - Anomaly detection results
- ``freshness_pipeline_log`` - Freshness monitoring logs
- ``timeliness_pipeline_execution_log`` - Timeliness monitoring logs

**Closure Tables:**

- ``address_lineage_closure`` - Hierarchical address lineage relationships
- ``pipeline_execution_closure`` - Hierarchical pipeline execution relationships

**Custom Enums:**

- ``DatePartEnum`` - Time period enums (MINUTE, HOUR, DAY, WEEK, MONTH, YEAR)
- ``AnomalyMetricFieldEnum`` - Anomaly detection metric fields

**Key Features Established:**

- Complete data lineage tracking system
- Anomaly detection infrastructure
- Freshness and timeliness monitoring
- Hierarchical execution relationships
- Performance metrics collection
- Comprehensive indexing for query optimization

Migration Structure
~~~~~~~~~~~~~~~~~~

Each migration file contains:

.. code-block:: python

   from typing import Sequence, Union
   import sqlalchemy as sa
   from alembic import op
   from sqlalchemy.dialects import postgresql

   revision: str = "20250128000000"
   down_revision: Union[str, Sequence[str], None] = "20250927222116"
   branch_labels: Union[str, Sequence[str], None] = None
   depends_on: Union[str, Sequence[str], None] = None

   def upgrade() -> None:
       # Migration logic here
       pass

   def downgrade() -> None:
       # Rollback logic here
       pass

Migration Commands
------------------

Basic Commands
~~~~~~~~~~~~~~

Check Current Status
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   alembic current

View Migration History
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   alembic history

Run Migrations
~~~~~~~~~~~~~~

.. code-block:: bash

   alembic upgrade head

Rollback Migrations
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   alembic downgrade -1

Create New Migration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   alembic revision -m "Description of changes"

Advanced Commands
~~~~~~~~~~~~~~~~

Upgrade to Specific Version
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   alembic upgrade 20250128000000

Downgrade to Specific Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   alembic downgrade 20250909185058

Show SQL for Migration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   alembic upgrade head --sql

Check for Pending Migrations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   alembic check

Migration Best Practices
------------------------

Development Workflow
~~~~~~~~~~~~~~~~~~~~

1. Create Migration
~~~~~~~~~~~~~~~~~~

   .. code-block:: bash

      alembic revision -m "Add new table"

2. Edit Migration File
~~~~~~~~~~~~~~~~~~~~

   - Add upgrade logic
   - Add downgrade logic
   - Test migration locally

3. Test Migration
~~~~~~~~~~~~~~~~

   .. code-block:: bash

      alembic upgrade head
      alembic downgrade -1
      alembic upgrade head

4. Commit Changes
~~~~~~~~~~~~~~~~

   .. code-block:: bash

      git add migrations/
      git commit -m "Add new table migration"

Production Deployment
~~~~~~~~~~~~~~~~~~~~~

Pre-deployment
~~~~~~~~~~~~~~

.. code-block:: bash

   # Backup database
   pg_dump $DATABASE_URL > backup.sql
   
   # Test migration
   alembic upgrade head --sql
   
   # Run migration
   alembic upgrade head

Post-deployment
~~~~~~~~~~~~~~

.. code-block:: bash

   # Verify migration
   alembic current
   
   # Check application
   curl http://localhost:8000

Migration Safety
----------------

Safe Operations
~~~~~~~~~~~~~~~

- Adding new columns with defaults
- Adding new tables
- Adding indexes
- Adding constraints (with validation)

Risky Operations
~~~~~~~~~~~~~~~~

- Dropping columns
- Changing column types
- Dropping tables
- Modifying constraints

Best Practices
~~~~~~~~~~~~~~

- Always backup before migrations
- Test migrations in development
- Use transactions for complex changes
- Validate data after migrations

Rollback Strategy
~~~~~~~~~~~~~~~~

Simple Rollbacks
~~~~~~~~~~~~~~~~

- Column additions
- Table additions
- Index additions

Complex Rollbacks
~~~~~~~~~~~~~~~~

- Data transformations
- Constraint changes
- Schema restructuring

Rollback Testing
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Test rollback
   alembic downgrade -1
   alembic upgrade head
   
   # Verify data integrity
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline;"

Production Management
----------------------

Production Deployment
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Set production database
   export DATABASE_URL="postgresql+asyncpg://user:password@prod-db:5432/watcher_prod"
   
   # Backup database
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # Run migrations
   alembic upgrade head
   
   # Verify migration
   alembic current

Rollback Production
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Rollback migration
   alembic downgrade -1
   
   # Verify rollback
   alembic current
   
   # Check application
   curl http://localhost:8000

Migration Troubleshooting
-------------------------

Common Issues
~~~~~~~~~~~~~

Migration Conflicts
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check for conflicts
   alembic check
   
   # Resolve conflicts
   alembic merge -m "Resolve conflicts"

Failed Migrations
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check migration status
   alembic current
   
   # Check migration history
   alembic history
   
   # Rollback failed migration
   alembic downgrade -1
   
   # Fix migration file
   # Re-run migration
   alembic upgrade head

Data Corruption
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Restore from backup
   psql $DATABASE_URL < backup.sql
   
   # Re-run migrations
   alembic upgrade head

Schema Drift
~~~~~~~~~~~~

.. code-block:: bash

   # Check schema drift
   alembic check
   
   # Generate new migration
   alembic revision --autogenerate -m "Fix schema drift"
   
   # Review generated migration
   # Run migration
   alembic upgrade head

Migration Automation
--------------------

GitHub Actions
~~~~~~~~~~~~~~

.. code-block:: yaml

   - name: Run Database Migrations
     run: |
       alembic upgrade head
       alembic current

Docker Integration
~~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   # Run migrations in Docker
   RUN alembic upgrade head

Migration Logging
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Enable migration logging
   export ALEMBIC_LOG_LEVEL=INFO
   
   # Run migrations with logging
   alembic upgrade head

Migration Tracking
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Track migration history
   alembic history
   
   # Check migration status
   alembic current
   
   # Monitor migration performance
   time alembic upgrade head

Alerting
~~~~~~~~

.. code-block:: bash

   # Check for failed migrations
   if ! alembic upgrade head; then
     echo "Migration failed"
     exit 1
   fi
   
   # Check for pending migrations
   if alembic check; then
     echo "Pending migrations found"
     exit 1
   fi

Best Practices Summary
----------------------

Migration Development
~~~~~~~~~~~~~~~~~~~~

- **Small Changes** Keep migrations focused and small
- **Test Thoroughly** Test migrations in development
- **Document Changes** Document migration purpose
- **Review Code** Review migration code before deployment

Migration Deployment
~~~~~~~~~~~~~~~~~~~~

- **Backup First** Always backup before migrations
- **Test Environment** Test in staging first
- **Rollback Plan** Have rollback strategy ready
- **Monitor Closely** Monitor during deployment

Migration Maintenance
~~~~~~~~~~~~~~~~~~~~

- **Regular Cleanup** Remove old migration files
- **Performance Monitoring** Monitor migration performance
- **Documentation** Keep migration documentation current
- **Training** Train team on migration procedures
