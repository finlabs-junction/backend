from __future__ import annotations

import logging
import typing as t

from litestar_saq import QueueConfig, SAQConfig, SAQPlugin

from litestar.config.cors import CORSConfig
from litestar.logging.config import LoggingConfig, StructLoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin

if t.TYPE_CHECKING:
    from qs.contrib.litestar.settings import (
        APISettings,
        SAQSettings,
        StructlogSettings,
    )


def create_cors_config(
    api_settings: APISettings,
) -> CORSConfig:
    return CORSConfig(
        allow_origins=api_settings.allow_origins,
        allow_credentials=True,
    )


def create_structlog_plugin(
    log_settings: StructlogSettings,
) -> StructlogPlugin:
    config = StructlogConfig(
        structlog_logging_config=StructLoggingConfig(
            log_exceptions="always",
            standard_lib_logging_config=LoggingConfig(
                root={
                    "level": logging.getLevelName(log_settings.level),
                    "handlers": ["queue_listener"],
                },
                loggers={
                    "granian.access": {
                        "propagate": False,
                        "level": log_settings.granian_access_level,
                        "handlers": ["queue_listener"],
                    },
                    "granian.error": {
                        "propagate": False,
                        "level": log_settings.granian_error_level,
                        "handlers": ["queue_listener"],
                    },
                    "sqlalchemy.engine": {
                        "propagate": False,
                        "level": log_settings.sqlalchemy_level,
                        "handlers": ["queue_listener"],
                    },
                    "sqlalchemy.pool": {
                        "propagate": False,
                        "level": log_settings.sqlalchemy_level,
                        "handlers": ["queue_listener"],
                    },
                },
            ),
        ),
        middleware_logging_config=LoggingMiddlewareConfig(
            request_cookies_to_obfuscate=log_settings.obfuscate_cookies,
            request_headers_to_obfuscate=log_settings.obfuscate_headers,
            request_log_fields=log_settings.request_fields,
            response_log_fields=log_settings.response_fields,
        ),
    )

    return StructlogPlugin(config=config)


def create_saq_plugin(
    settings: SAQSettings,
    queue_configs: t.Collection[QueueConfig],
) -> SAQPlugin:
    return SAQPlugin(config=SAQConfig(
        web_enabled=settings.web_enabled,
        worker_processes=settings.processes,
        use_server_lifespan=settings.use_server_lifespan,
        queue_configs=queue_configs,
    ))
