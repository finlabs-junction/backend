from __future__ import annotations

from qs.contrib.msgspec import *


class SessionCreateRequest(Struct):
    username: str


class SessionCreateResponse(Struct):
    session_id: str


class SessionJoinRequest(Struct):
    username: str


class PollResponse(Struct):
    session_id: str
    username: str
