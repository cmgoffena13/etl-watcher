import uuid
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    LOGFIRE_TOKEN: Optional[str] = None
    LOGFIRE_CONSOLE: Optional[str] = None
    LOGFIRE_IGNORE_NO_CONFIG: Optional[bool] = False
    SLACK_WEBHOOK_URL: Optional[str] = None
    WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES: Optional[bool] = False
    WATCHER_TIMELINESS_CHECK_LOOKBACK_MINUTES: Optional[int] = 60
    WATCHER_TIMELINESS_CHECK_SCHEDULE: Optional[str] = (
        "*/15 * * * *"  # Every 15 minutes
    )
    WATCHER_FRESHNESS_CHECK_SCHEDULE: Optional[str] = "0 * * * *"  # Every hour at :00
    WATCHER_CELERY_QUEUE_HEALTH_CHECK_SCHEDULE: Optional[str] = (
        "*/5 * * * *"  # Every 5 minutes
    )
    PROFILING_ENABLED: Optional[bool] = False
    REDIS_URL: Optional[str] = None


class DevConfig(GlobalConfig):
    PROFILING_ENABLED: Optional[bool] = True
    LOGFIRE_CONSOLE: Optional[bool] = False
    REDIS_URL: Optional[str] = "redis://redis:6379/1"

    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestConfig(GlobalConfig):
    WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES: Optional[bool] = False
    SLACK_WEBHOOK_URL: Optional[str] = (
        "https://hooks.slack.com/services/test/dummy/webhook"
    )
    LOGFIRE_IGNORE_NO_CONFIG: Optional[bool] = True
    model_config = SettingsConfigDict(env_prefix="TEST_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


@lru_cache()
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)


def get_database_config():
    """Get database configuration for both SQLAlchemy and Alembic"""
    env_state = BaseConfig().ENV_STATE
    db_config = get_config(env_state)

    if db_config.DATABASE_URL is None:
        env_prefix = {"dev": "DEV_", "test": "TEST_", "prod": "PROD_"}.get(
            env_state, ""
        )
        raise ValueError(
            f"{env_prefix}DATABASE_URL is not set for the {env_state} environment"
        )

    config_dict = {
        "sqlalchemy.url": db_config.DATABASE_URL,
        "sqlalchemy.echo": True if isinstance(config, DevConfig) else False,
        "sqlalchemy.future": True,
        "sqlalchemy.pool_size": 20,
        "sqlalchemy.max_overflow": 10,
        "sqlalchemy.pool_timeout": 30,
    }

    # Add database-specific connect args
    if db_config.DATABASE_URL.startswith("sqlite"):
        config_dict["sqlalchemy.connect_args"] = {"check_same_thread": False}
    elif isinstance(db_config, TestConfig):
        # PostgreSQL settings for pgbouncer compatibility in test environment
        config_dict["sqlalchemy.connect_args"] = {
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
            "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
            "command_timeout": 60,  # Increase timeout for test teardown
        }

    return config_dict
