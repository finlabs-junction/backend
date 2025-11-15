from __future__ import annotations

from litestar import Request
from authlib.jose import jwt

from qs.contrib.litestar import *
from qs.cache import lru_cache
from qs.game.session import Session, Player
from qs.server import get_settings
from qs.exceptions import UnauthorizedError


def get_dependencies() -> dict[str, Provide]:
    return {
        "session": Provide(provide_session, sync_to_thread=False),
        "player": Provide(provide_player, sync_to_thread=False),
    }


@lru_cache(maxsize=1024, ttl=3600)
def get_session(session_id: str) -> Session:
    return Session(session_id=session_id)


def provide_session(session_id: str) -> Session:
    return get_session(session_id)


def provide_player(request: Request) -> Player:
    settings = get_settings()

    if settings.api.debug:
        key = "token"
    else:
        key = "__Session-token"

    token = request.cookies.get(key)

    if token is None:
        raise UnauthorizedError()
    
    payload = jwt.decode(
        token,
        settings.api.jwt_secret_key,
    )

    username = payload["username"]
    session_id = payload["session_id"]

    session = get_session(session_id)
    return session.get_player(username)
