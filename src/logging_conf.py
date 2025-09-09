import logging
from logging.config import dictConfig

import logfire
from logfire import LogfireLoggingHandler

from src.settings import DevConfig, config

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logfire.configure(token=config.LOGFIRE_TOKEN, service_name="watcher")

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(name)s:%(lineno)d - %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                },
                "logfire_src": {
                    "class": LogfireLoggingHandler,
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                },
                "logfire_sql": {
                    "class": LogfireLoggingHandler,
                    "level": "INFO",
                },
            },
            "loggers": {
                "src": {
                    "handlers": ["default", "logfire_src"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "sqlalchemy.engine": {
                    "handlers": ["logfire_sql"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )

    logger.info("Logging Configuration Successful")
