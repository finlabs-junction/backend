from __future__ import annotations

import typing as t
import secrets

from litestar import Response
from authlib.jose import jwt

from qs.contrib.litestar import *
from qs.server import get_settings
from qs.server.exceptions import *
from qs.server.schemas import *
from qs.server.services import *
from qs.game.session import Session, Player
from qs.server.dependencies import get_session


def get_routes() -> list[ControllerRouterHandler]:
    return [
        SessionController,
        poll,
    ]


def create_token(session_id: str, username: str) -> str:
    settings = get_settings()

    payload = {
        "session_id": session_id,
        "username": username,
    }

    token = jwt.encode(
        {"alg": "HS256"},
        payload,
        settings.api.jwt_secret_key,
    )

    return token.decode("utf-8")


def create_session() -> Session:
    session_id = secrets.token_hex(3).upper()
    return get_session(session_id)


def set_token_in_response(
    response: Response,
    token: str,
) -> None:
    settings = get_settings()

    if settings.api.debug:
        key = "token"
        secure = False
        samesite = "strict"
    else:
        key = "__Session-token"
        secure = True
        samesite = "none"

    response.set_cookie(
        key=key,
        value=token,
        httponly=True,
        secure=secure,
        samesite=samesite,
    )


class SessionController(Controller):
    path = "/session"
    tags = ["Session"]
    signature_types = [Session, Player]

    @post(
        operation_id="SessionCreate",
        path="/create"
    )
    async def create(
        self,
        data: SessionCreateRequest,
    ) -> Response[SessionCreateResponse]:
        session = create_session()

        session.add_player(data.username)

        token = create_token(
            session_id=session.get_id(),
            username=data.username,
        )

        content = SessionCreateResponse(
            session_id=session.get_id(),
        )

        response = Response(content)
        set_token_in_response(response, token)

        return response

    @post(
        operation_id="SessionJoin",
        path="/{session_id:str}/join",
    )
    async def join(
        self,
        session: Session,
        data: SessionJoinRequest,
    ) -> Response:
        session.add_player(data.username)

        token = create_token(
            session_id=session.get_id(),
            username=data.username,
        )

        response = Response(None)
        set_token_in_response(response, token)

        return response

    @get(
        operation_id="logout",
        path="/logout",
    )
    async def logout(
        self,
        player: Player,
    ) -> Response:
        # just remove the cookie storing the token
        response = Response(None)
        set_token_in_response(response, "")

        return response


@get(
    operation_id="Poll",
    path="/poll",
    tags=["Poll"],
)
async def poll(player: Player) -> PollResponse:
    session = player.get_session()

    return PollResponse(
        session_id=session.get_id(),
        username=player.get_username(),
    )
