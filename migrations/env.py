import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import DateTime, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel  # ADDED

# Have to import each sqlmodel to ensure its part of metadata
from src.database import *  # ADDED
from src.settings import get_database_config  # ADDED

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata  # UPDATED


# Customize DateTime column generation for timezone support
def include_object(object, name, type_, reflected, compare_to):
    return True


def render_item(type_, obj, autogen_context):
    if type_ == "type" and isinstance(obj, DateTime):
        return "sa.DateTime(timezone=True)"
    return False


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use your centralized database config
    db_config = get_database_config()  # ADDED
    url = db_config["sqlalchemy.url"]  # ADDED
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # Use your centralized database config
    db_config = get_database_config()  # ADDED

    connectable = create_async_engine(
        url=db_config["sqlalchemy.url"],
        echo=db_config["sqlalchemy.echo"],
        future=db_config["sqlalchemy.future"],
        connect_args=db_config.get("sqlalchemy.connect_args", {}),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
