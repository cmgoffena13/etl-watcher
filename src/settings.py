from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    LOGFIRE_TOKEN: Optional[str] = None
    LOGFIRE_CONSOLE: Optional[bool] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES: Optional[bool] = False


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestConfig(GlobalConfig):
    TEST_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES: False
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
    }

    # Add SQLite-specific settings if using SQLite
    if db_config.DATABASE_URL.startswith("sqlite"):
        config_dict["sqlalchemy.connect_args"] = {"check_same_thread": False}

    return config_dict
