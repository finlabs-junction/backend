from __future__ import annotations

import os

from advanced_alchemy.extensions.litestar import (
    AlembicAsyncConfig,
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)
from msgspec import Struct
from qs.contrib.sqlalchemy.engine import create_engine


class SQLAlchemyEngineSettings(Struct):
    url: str = os.environ.get(
        "QS_SQLALCHEMY_URL",
        "postgresql+asyncpg://user:password@host:5432/database",
    )
    """
    SQLAlchemy Database URL.
    """

    echo: bool = False
    """
    Enable SQLAlchemy engine logs.
    """

    echo_pool: bool = False
    """
    Enable SQLAlchemy pool logs.
    """

    pool_disabled: bool = False
    """
    Disable SQLAlchemy pool configuration.
    """

    pool_max_overflow: int = 10
    """
    Max overflow for SQLAlchemy connection pool.
    """

    pool_size: int = 5
    """
    Pool size for SQLAlchemy connection pool.
    """

    pool_timeout: int = 30
    """
    Time in seconds for timing connections out of the connection pool.
    """

    pool_recycle: int = 300
    """
    Seconds to wait before recycling connections.
    """

    pool_pre_ping: bool = False
    """
    Optionally ping database before fetching a session from the connection pool.
    """


class SQLAlchemySettings(SQLAlchemyEngineSettings):
    migration_config: str = "db/alembic.ini"
    """
    The path to the `alembic.ini` configuration file.
    """

    migration_path: str = "db/migrations"
    """
    The path to the `alembic` migration directory.
    """

    migration_ddl_version_table: str = "ddl_version"
    """
    The name to use for the `alembic` versions table name.
    """

    fixture_path: str = "db/fixtures"
    """
    The path to JSON fixture files to load into tables.
    """


def create_sqlalchemy_config(
    settings: SQLAlchemySettings,
) -> SQLAlchemyAsyncConfig:
    return SQLAlchemyAsyncConfig(
        engine_instance=create_engine(settings),
        before_send_handler="autocommit",
        session_config=AsyncSessionConfig(expire_on_commit=False),
        alembic_config=AlembicAsyncConfig(
            version_table_name=settings.migration_ddl_version_table,
            script_config=str(settings.migration_config),
            script_location=str(settings.migration_path),
        ),
    )
