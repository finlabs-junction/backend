from __future__ import annotations

import asyncio
from datetime import datetime, date, timedelta
from enum import StrEnum

from qs.game.player import Player
from qs.exceptions import (
    PlayerNotFoundError,
    PlayerAlreadyExistsError,
)
from qs.game.stocks import get_stock_prices


class SessionStatus(StrEnum):
    WAITING = "waiting"
    RUNNING = "running"
    ENDED = "ended"


class Session:
    def __init__(
        self, 
        session_id: str,
        period: tuple[datetime, datetime],
        stock_prices: dict[str, dict[date, float]],
    ):
        self._id = session_id
        self._players: dict[str, Player] = {}
        self._time, self._end_time = period
        self._stock_prices = stock_prices
        self._time_progression_multiplier = 1
        self._task: asyncio.Task | None = None


    @classmethod
    async def create_scenario_2008(cls, session_id: str) -> Session:
        start_time = datetime(2008, 1, 1, 12, 0, 0)
        end_time = datetime(2008, 3, 1, 12, 0, 0)

        stock_prices = await get_stock_prices(
            symbols=("AAPL", "GOOGL", "MSFT", "AMZN"),
            period=(start_time, end_time),
        )

        return cls(
            session_id=session_id,
            period=(start_time, end_time),
            stock_prices=stock_prices,
        )


    def get_id(self) -> str:
        return self._id
    

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


    def start(self) -> None:
        if self._task is not None:
            return

        async def run():
            while self._time < self._end_time:
                for _ in range(self._time_progression_multiplier):
                    self.tick()

                await asyncio.sleep(1)

        loop = asyncio.get_running_loop()
        self._task = loop.create_task(run())
    

    def get_status(self) -> SessionStatus:
        if self._task is None:
            return SessionStatus.WAITING
        
        if self._task.done():
            return SessionStatus.ENDED
        
        return SessionStatus.RUNNING


    def get_stock_price(self, symbol: str) -> float:
        prices = self._stock_prices[symbol]
        current_date = self._time.date()
        first_date = min(prices.keys())

        while current_date >= first_date:
            if current_date in prices:
                return prices[current_date]
            
            current_date -= timedelta(days=1)

        return prices[first_date]


    def get_stock_prices(self) -> dict[str, dict[date, float]]:
        return self._stock_prices
