from __future__ import annotations

import os
import secrets

import msgspec
from msgspec import Struct
from qs.contrib.redis.settings import RedisSettings
from qs.contrib.sqlalchemy.settings import SQLAlchemySettings

from litestar.data_extractors import (
    RequestExtractorField,
    ResponseExtractorField,
)

TRUE_VALUES = {"True", "true", "1"}


class APISettings(Struct):
    app_name: str = "qualityslop API"
    """
    Application name displayed e.g. in the OpenAPI documentation.
    """

    debug: bool = os.environ.get("QS_DEBUG", "False") in TRUE_VALUES
    """
    If True, `Litestar` will be run in debug mode. Do not use in production.
    Other behaviour may depend on it as well, look for references.
    """

    jwt_secret_key: str = msgspec.field(
        default_factory=lambda: os.environ.get(
            "QS_JWT_SECRET_KEY",
            secrets.token_urlsafe(32),
        ),
    )
    """
    Application secret key for signing JWTs.
    """

    allow_origins: list[str] = msgspec.field(
        default_factory=lambda: list(os.environ.get(
            "QS_ALLOW_ORIGINS",
            ["http://localhost:8000"],
        )),
    )
    """
    List of allowed origins for CORS.
    """

    base_url: str = os.environ.get(
        "QS_BASE_URL",
        "http://localhost:8000",
    )
    """
    Base URL of the application without a trailing slash.
    """

    cache_expiration: int = int(os.environ.get("QS_CACHE_EXPIRATION", 60))
    """
    Expiration time for cached responses in seconds.
    """


class SSOProviderSettings(Struct):
    client_id: str = os.environ.get("QS_GOOGLE_CLIENT_ID", "")
    """
    OAuth2 client ID assigned by the provider.
    """

    client_secret: str = os.environ.get("QS_GOOGLE_CLIENT_SECRET", "")
    """
    OAuth2 client secret assigned by the provider.
    """


class SSOSettings(Struct):
    google: SSOProviderSettings = msgspec.field(
        default_factory=SSOProviderSettings,
    )
    """
    Google OAuth2 credentials for Single Sign-On.
    """


class StructlogSettings(Struct):
    exclude_paths: str = r"\A(?!x)x" # exclude nothing
    """
    Regex to exclude paths from logging.
    """

    http_event: str = "HTTP"
    """
    Log event name for logs from Litestar handlers.
    """

    include_compressed_body: bool = False
    """
    Include body of compressed responses in log output.
    """

    level: int = 20
    """
    Stdlib log levels. Only emit logs at this level, or higher.
    """

    obfuscate_cookies: set[str] = msgspec.field(
        default_factory=lambda: {"__Secure-JWT", "JWT"},
    )
    """
    Request cookie keys to obfuscate.
    """

    obfuscate_headers: set[str] = msgspec.field(
        default_factory=lambda: {"Authorization"},
    )
    """
    Request header keys to obfuscate.
    """

    request_fields: list[RequestExtractorField] = msgspec.field(
        default_factory=lambda: [
            "path",
            "method",
            "headers",
            "cookies",
            "query",
            "path_params",
            "body",
        ],
    )
    """
    Attributes of the request to be logged.
    """

    response_fields: list[ResponseExtractorField] = msgspec.field(
        default_factory=lambda: [
            "status_code",
            "cookies",
            "headers",
            "body",
        ],
    )
    """
    Attributes of the response to be logged.
    """

    sqlalchemy_level: int = 30
    """
    Level to log SQLAlchemy logs.
    """

    granian_access_level: int = 30
    """
    Level to log granian access logs.
    """

    granian_error_level: int = 20
    """
    Level to log granian error logs.
    """


class SAQSettings(msgspec.Struct):
    processes: int = 1
    """
    Number of worker processes to spawn.
    """

    threads: int = 1
    """
    Number of concurrent jobs allowed per worker process.
    """

    web_enabled: bool = True
    """
    If True, the worker admin UI is enabled.
    """

    use_server_lifespan: bool = True
    """
    Start the worker processes with the Litestar application.
    """


class AppSettings(Struct):
    api: APISettings = msgspec.field(default_factory=APISettings)
    """
    API settings.
    """

    sso: SSOSettings = msgspec.field(default_factory=SSOSettings)
    """
    Single sign-on settings.
    """

    structlog: StructlogSettings = msgspec.field(
        default_factory=StructlogSettings,
    )
    """
    Structlog settings.
    """

    saq: SAQSettings = msgspec.field(default_factory=SAQSettings)
    """
    SAQ settings.
    """

    redis: RedisSettings = msgspec.field(default_factory=RedisSettings)
    """
    Redis settings.
    """

    sqlalchemy: SQLAlchemySettings = msgspec.field(
        default_factory=SQLAlchemySettings,
    )
    """
    SQLAlchemy settings.
    """
