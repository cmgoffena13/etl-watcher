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
    PROFILING_ENABLED: Optional[bool] = False
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None


class DevConfig(GlobalConfig):
    PROFILING_ENABLED: Optional[bool] = True
    LOGFIRE_CONSOLE: Optional[bool] = False
    REDIS_HOST: Optional[str] = "redis"
    REDIS_PORT: Optional[int] = 6379
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
    db_config = get_config(BaseConfig().ENV_STATE)

    config_dict = {
        "sqlalchemy.url": db_config.DATABASE_URL,
        "sqlalchemy.echo": True if isinstance(config, DevConfig) else False,
        "sqlalchemy.future": True,
        "sqlalchemy.pool_size": 20,
        "sqlalchemy.max_overflow": 10,
        "sqlalchemy.pool_timeout": 30,
    }

    # Add SQLite-specific settings if using SQLite
    if db_config.DATABASE_URL.startswith("sqlite"):
        config_dict["sqlalchemy.connect_args"] = {"check_same_thread": False}

    return config_dict
