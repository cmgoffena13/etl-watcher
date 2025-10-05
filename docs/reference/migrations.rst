Database Migrations
====================

This section covers database migration management in Watcher.

Migration Overview
------------------

Watcher uses Alembic for database migration management:

- **Version Control** Track schema changes over time
- **Rollback Support** Revert schema changes when needed
- **Data Preservation** Maintain data integrity during changes
- **Environment Management** Handle different environments

Migration Files
---------------

Current Migrations
~~~~~~~~~~~~~~~~~~

**Initial Migration** (20250909185058_initial.py):
- Creates all core tables
- Sets up indexes and constraints
- Establishes basic schema structure

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
   curl http://localhost:8000/health

Migration Safety
----------------

Data Preservation
~~~~~~~~~~~~~~~~

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

Migration Examples
------------------

Adding a New Column
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def upgrade() -> None:
       op.add_column('pipeline', sa.Column('new_field', sa.String(255), nullable=True))

   def downgrade() -> None:
       op.drop_column('pipeline', 'new_field')

Adding a New Table
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def upgrade() -> None:
       op.create_table('new_table',
           sa.Column('id', sa.Integer(), nullable=False),
           sa.Column('name', sa.String(255), nullable=False),
           sa.PrimaryKeyConstraint('id')
       )

   def downgrade() -> None:
       op.drop_table('new_table')

Adding an Index
~~~~~~~~~~~~~~~

.. code-block:: python

   def upgrade() -> None:
       op.create_index('ix_new_table_name', 'new_table', ['name'])

   def downgrade() -> None:
       op.drop_index('ix_new_table_name', table_name='new_table')

Adding a Constraint
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def upgrade() -> None:
       op.create_check_constraint('ck_new_table_name', 'new_table', 'name IS NOT NULL')

   def downgrade() -> None:
       op.drop_constraint('ck_new_table_name', 'new_table', type_='check')

Data Migration
~~~~~~~~~~~~~~

.. code-block:: python

   def upgrade() -> None:
       # Add new column
       op.add_column('pipeline', sa.Column('new_field', sa.String(255), nullable=True))
       
       # Migrate data
       connection = op.get_bind()
       connection.execute(
           "UPDATE pipeline SET new_field = 'default_value' WHERE new_field IS NULL"
       )
       
       # Make column not null
       op.alter_column('pipeline', 'new_field', nullable=False)

   def downgrade() -> None:
       op.drop_column('pipeline', 'new_field')

Environment Management
----------------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~

Local Development
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Set development database
   export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/watcher_dev"
   
   # Run migrations
   alembic upgrade head

Docker Development
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use Docker database
   export DATABASE_URL="postgresql+asyncpg://user:password@postgres:5432/watcher_dev"
   
   # Run migrations
   alembic upgrade head

Testing Environment
~~~~~~~~~~~~~~~~~~~~

Test Database
~~~~~~~~~~~~~

.. code-block:: bash

   # Set test database
   export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/watcher_test"
   
   # Run migrations
   alembic upgrade head
   
   # Run tests
   uv run pytest

Test Isolation
~~~~~~~~~~~~~~

.. code-block:: bash

   # Reset test database
   dropdb watcher_test
   createdb watcher_test
   alembic upgrade head

Production Environment
~~~~~~~~~~~~~~~~~~~~~~~

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
   curl http://localhost:8000/health

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

Migration Validation
--------------------

Pre-Migration Checks
~~~~~~~~~~~~~~~~~~~~

Schema Validation
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check current schema
   psql $DATABASE_URL -c "\d"
   
   # Check migration status
   alembic current
   
   # Check for pending migrations
   alembic check

Data Validation
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check data integrity
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline;"
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline_execution;"
   
   # Check for orphaned records
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline_execution WHERE pipeline_id NOT IN (SELECT id FROM pipeline);"

Post-Migration Checks
~~~~~~~~~~~~~~~~~~~~~

Schema Verification
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check new schema
   psql $DATABASE_URL -c "\d"
   
   # Check indexes
   psql $DATABASE_URL -c "SELECT indexname FROM pg_indexes WHERE tablename = 'pipeline';"
   
   # Check constraints
   psql $DATABASE_URL -c "SELECT conname FROM pg_constraint WHERE conrelid = 'pipeline'::regclass;"

Data Verification
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check data integrity
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline;"
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline_execution;"
   
   # Check new data
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM pipeline WHERE new_field IS NOT NULL;"

Application Verification
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check application health
   curl http://localhost:8000/health
   
   # Check API endpoints
   curl http://localhost:8000/pipeline
   
   # Check diagnostics
   curl http://localhost:8000/diagnostics

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

Migration Monitoring
~~~~~~~~~~~~~~~~~~~~

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
