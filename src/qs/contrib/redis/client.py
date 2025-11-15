from __future__ import annotations

import typing as t

from redis.asyncio import Redis

if t.TYPE_CHECKING:
    from qs.contrib.redis.settings import RedisSettings


def create_redis_client(settings: RedisSettings) -> Redis:
    return Redis.from_url(
        url=settings.url,
        encoding="utf-8",
        decode_responses=False,
        socket_connect_timeout=settings.socket_connect_timeout,
        socket_keepalive=settings.socket_keepalive,
        health_check_interval=settings.health_check_interval,
    )
