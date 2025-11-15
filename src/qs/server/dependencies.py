from __future__ import annotations

from qs.contrib.litestar import *
from qs.cache import lru_cache
from qs.game.session import Session


def get_dependencies() -> dict[str, Provide]:
    return {
        "session": Provide(provide_session, sync_to_thread=False),
    }


@lru_cache(maxsize=1024, ttl=3600)
def get_session(session_id: str) -> Session:
    return Session()


def provide_session(session_id: str) -> Session:
    return get_session(session_id)
