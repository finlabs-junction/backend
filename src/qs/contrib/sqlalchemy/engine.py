from __future__ import annotations

import typing as t

from litestar.serialization import decode_json, encode_json

from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

if t.TYPE_CHECKING:
    from qs.contrib.sqlalchemy.settings import SQLAlchemyEngineSettings

    from sqlalchemy.ext.asyncio import AsyncEngine


def create_engine(settings: SQLAlchemyEngineSettings) -> AsyncEngine:
    if settings.url.startswith("postgresql+asyncpg"):
        engine = create_async_engine(
            url=settings.url,
            future=True,
            json_serializer=encode_json,
            json_deserializer=decode_json,
            echo=settings.echo,
            echo_pool=settings.echo_pool,
            max_overflow=settings.pool_max_overflow,
            pool_size=settings.pool_size,
            pool_timeout=settings.pool_timeout,
            pool_recycle=settings.pool_recycle,
            pool_pre_ping=settings.pool_pre_ping,
            pool_use_lifo=True, # use lifo to reduce the number of idle connections # noqa: E501
            poolclass=NullPool if settings.pool_disabled else None,
        )

        @event.listens_for(engine.sync_engine, "connect")
        def _sqla_on_connect(
            dbapi_connection: t.Any, _: t.Any,
        ) -> t.Any:  # pragma: no cover
            """
            Using msgspec for serialization of the json column values means that the
            output is binary, not `str` like `json.dumps` would output.
            SQLAlchemy expects that the json serializer returns `str` and calls `.encode()` on the value to
            turn it to bytes before writing to the JSONB column. I'd need to either wrap `serialization.to_json` to
            return a `str` so that SQLAlchemy could then convert it to binary, or do the following, which
            changes the behaviour of the dialect to expect a binary value from the serializer.
            See Also https://github.com/sqlalchemy/sqlalchemy/blob/14bfbadfdf9260a1c40f63b31641b27fe9de12a0/lib/sqlalchemy/dialects/postgresql/asyncpg.py#L934
            """ # noqa: E501, D401

            def encoder(bin_value: bytes) -> bytes:
                return b"\x01" + encode_json(bin_value)

            def decoder(bin_value: bytes) -> t.Any:
                # the byte is the \x01 prefix for jsonb used by PostgreSQL.
                # asyncpg returns it when format='binary'
                return decode_json(bin_value[1:])

            dbapi_connection.await_(
                dbapi_connection.driver_connection.set_type_codec(
                    "jsonb",
                    encoder=encoder,
                    decoder=decoder,
                    schema="pg_catalog",
                    format="binary",
                ),
            )
            dbapi_connection.await_(
                dbapi_connection.driver_connection.set_type_codec(
                    "json",
                    encoder=encoder,
                    decoder=decoder,
                    schema="pg_catalog",
                    format="binary",
                ),
            )
    else:
        engine = create_async_engine(
            url=settings.url,
            future=True,
            json_serializer=encode_json,
            json_deserializer=decode_json,
            echo=settings.echo,
            echo_pool=settings.echo_pool,
            max_overflow=settings.pool_max_overflow,
            pool_size=settings.pool_size,
            pool_timeout=settings.pool_timeout,
            pool_recycle=settings.pool_recycle,
            pool_pre_ping=settings.pool_pre_ping,
        )

    return engine
