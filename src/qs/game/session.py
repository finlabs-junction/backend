from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from enum import StrEnum

from qs.game.player import Player
from qs.exceptions import (
    PlayerNotFoundError,
    PlayerAlreadyExistsError,
)


class SessionStatus(StrEnum):
    WAITING = "waiting"
    RUNNING = "running"
    ENDED = "ended"


class Session:
    def __init__(self, session_id: str):
        self._id = session_id
        self._players: dict[str, Player] = {}
        self._time = datetime(2007, 12, 2, 12, 0, 0)
        self._time_progression_multiplier = 1
        self._task: asyncio.Task | None = None

    def get_id(self) -> str:
        return self._id

    def get_players(self) -> list[Player]:
        return list(self._players.values())

    def get_player(self, username: str) -> Player:
        player = self._players.get(username)

        if player is None:
            raise PlayerNotFoundError(
                session_id=self._id,
                username=username,
            )

        return player

    def add_player(
        self,
        username: str,
        is_leader: bool = False,
    ) -> Player:
        player = Player(
            session=self,
            username=username,
            is_leader=is_leader,
        )

        if username in self._players:
            raise PlayerAlreadyExistsError(
                session_id=self._id,
                username=username,
            )

        self._players[username] = player

        return player

    def get_time(self) -> datetime:
        return self._time

    def get_time_progression_multiplier(self) -> int:
        return self._time_progression_multiplier

    def set_time_progression_multiplier(self, multiplier: int) -> None:
        self._time_progression_multiplier = multiplier

    def tick(self) -> None:
        self._time += timedelta(hours=1)

        for player in self._players.values():
            player.tick()

    def start(self, resume: bool = False) -> None:
        if self._task is not None:
            return

        async def run():
            if not resume:
                #  Gathering initial 30 days of ticks
                for _ in range(30 * 24):
                    self.tick()

            while True:
                for _ in range(self._time_progression_multiplier):
                    self.tick()

                await asyncio.sleep(1)

        loop = asyncio.get_running_loop()
        self._task = loop.create_task(run())

    def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            self._task = None

    def get_status(self) -> SessionStatus:
        if self._task is None:
            return SessionStatus.WAITING

        if self._task.done():
            return SessionStatus.ENDED

        return SessionStatus.RUNNING
