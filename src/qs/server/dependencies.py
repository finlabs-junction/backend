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
        "session": Provide(provide_session),
        "player": Provide(provide_player),
        "leader": Provide(provide_leader),
    }


@lru_cache(maxsize=1024, ttl=3600)
async def get_session(session_id: str) -> Session:
    return await Session.create_scenario_2008(session_id=session_id)


async def provide_session(session_id: str) -> Session:
    return await get_session(session_id)


async def provide_player(request: Request) -> Player:
    settings = get_settings()
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedError()
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    if not token:
        raise UnauthorizedError()
    
    try:
        payload = jwt.decode(
            token,
            settings.api.jwt_secret_key,
        )

        username = payload["username"]
        session_id = payload["session_id"]
    except Exception:
        raise UnauthorizedError()

    session = await get_session(session_id)
    return session.get_player(username)


async def provide_leader(player: Player) -> Player:
    if not player.is_leader():
        raise UnauthorizedError()
    
    return player
