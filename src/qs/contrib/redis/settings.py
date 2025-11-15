from __future__ import annotations

import os

from msgspec import Struct


class RedisSettings(Struct):
    url: str = os.environ.get("QS_REDIS_URL", "redis://localhost:6379/0")
    """
    A Redis connection URL.
    """

    socket_connect_timeout: int = 5
    """
    Seconds to wait for a connection to become active.
    """

    health_check_interval: int = 5
    """
    Seconds to wait before testing connection health.
    """

    socket_keepalive: int = 60
    """
    Length of time to wait (in seconds) between keepalive commands.
    """
