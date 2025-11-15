from __future__ import annotations

from qs.exceptions import (
    PlayerNotFoundError,
    PlayerAlreadyExistsError,
)


class Session:
    def __init__(self, session_id: str):
        self._id = session_id
        self._players: dict[str, Player] = {}


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
    

    def add_player(self, username: str) -> Player:
        player = Player(
            session=self,
            username=username,
        )

        if username in self._players:
            raise PlayerAlreadyExistsError(
                session_id=self._id,
                username=username,
            )

        self._players[username] = player

        return player
        

class Player:
    def __init__(
        self,
        session: Session,
        username: str,
    ):
        self._session = session
        self._username = username


    def get_session(self) -> Session:
        return self._session


    def get_username(self) -> str:
        return self._username
