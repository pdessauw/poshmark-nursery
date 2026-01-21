"""Logging configuration"""

import logging.config

from library.settings import BASE_DIR

LOGGER_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s][%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": f"{BASE_DIR}/debug.log",
            "maxBytes": 25000,
            "backupCount": 3,
        },
    },
    "loggers": {
        "app": {"level": "INFO", "handlers": ["console", "file"], "propagate": "no"}
    },
}

logging.config.dictConfig(LOGGER_CONFIG)
LOGGER = logging.getLogger("app")
