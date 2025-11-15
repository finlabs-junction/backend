from __future__ import annotations

import typing as t
import secrets

from litestar import Response
from authlib.jose import jwt

from qs.contrib.litestar import *
from qs.server import get_settings
from qs.server.schemas import *
from qs.server.services import *
from qs.game.session import Session
from qs.game.player import Player
from qs.server.dependencies import get_session


def get_routes() -> list[ControllerRouterHandler]:
    return [
        SessionController,
        GameController,
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


async def create_session() -> Session:
    session_id = secrets.token_hex(3).upper()
    return await get_session(session_id)


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
    tags = ["Sessions"]
    signature_types = [Session, Player]

    @post(
        operation_id="SessionCreate",
        path="/create"
    )
    async def create(
        self,
        data: SessionCreateRequest,
    ) -> Response[SessionCreateResponse]:
        session = await create_session()

        session.add_player(data.username, is_leader=True)

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
        operation_id="Logout",
        path="/logout",
    )
    async def logout(self) -> Response:
        response = Response(None)
        response.delete_cookie(key="__Session-token")
        response.delete_cookie(key="token")
        return response
    

class GameController(Controller):
    tags = ["Game"]
    signature_types = [Player]


    @post(
        operation_id="StartSession",
        path="/start",
    )
    async def start(
        self,
        leader: Player,
    ) -> None:
        session = leader.get_session()
        session.start()


    @get(
        operation_id="Poll",
        path="/poll",
    )
    async def poll(
        self,
        player: Player,
    ) -> PollResponse:
        session = player.get_session()

        stocks = [
            Position(
                symbol=symbol,
                last_price=session.get_stock_price(symbol),
                size=player.get_position_size(symbol),
                entry_price=player.get_position_entry_price(symbol),
                pnl=player.get_position_pnl(symbol),
            )
            for symbol in session.get_stock_prices().keys()
        ]

        return PollResponse(
            session_id=session.get_id(),
            session_status=session.get_status(),
            username=player.get_username(),
            is_leader=player.is_leader(),
            time=session.get_time(),
            time_progression_multiplier=session.get_time_progression_multiplier(),
            balance=player.get_balance(),
            monthly_income=player.get_monthly_income(),
            monthly_expenses=player.get_monthly_expenses(),
            monthly_net_income=player.get_monthly_net_income(),
            occupation=player.get_occupation().value,
            monthly_salary=player.get_monthly_salary(),
            health_level=player.get_health_level(),
            happiness_level=player.get_happiness_level(),
            energy_level=player.get_energy_level(),
            social_life_level=player.get_social_life_level(),
            stress_level=player.get_stress_level(),
            living_comfort_level=player.get_living_comfort_level(),
            monthly_rent_expense=player.get_monthly_rent_expense(),
            monthly_utilities_expense=player.get_monthly_utilities_expense(),
            monthly_grocery_expense=player.get_monthly_grocery_expense(),
            monthly_transportation_expense=player.get_monthly_transportation_expense(),
            monthly_leisure_expense=player.get_monthly_leisure_expense(),
            monthly_loan_expense=player.get_monthly_loan_expense(),
            monthly_tax_expense=player.get_monthly_tax_expense(),
            stocks=stocks,
        )


    @post(
        operation_id="SetTimeProgressionMultiplier",
        path="/set-time-progression-multiplier",
    )
    async def set_time_progression_multiplier(
        self,
        leader: Player,
        data: int,
    ) -> None:
        session = leader.get_session()
        session.set_time_progression_multiplier(data)


    @post(
        operation_id="SetMonthlyGroceryExpense",
        path="/set-monthly-grocery-expense",
    )
    async def set_monthly_grocery_expense(
        self,
        player: Player,
        data: float,
    ) -> None:
        player.set_monthly_grocery_expense(data)

    
    @post(
        operation_id="SetMonthlyLeisureExpense",
        path="/set-monthly-leisure-expense",
    )
    async def set_monthly_leisure_expense(
        self,
        player: Player,
        data: float,
    ) -> None:
        player.set_monthly_leisure_expense(data)


    @get(
        operation_id="GetStockPrices",
        path="/stock-prices",
    )
    async def get_stock_prices(
        self,
        player: Player,
    ) -> dict[str, dict[date, float]]:
        session = player.get_session()
        return session.get_stock_prices()


    @post(
        operation_id="BuyStock",
        path="/stock/{symbol:str}/buy",
    )
    async def buy_stock(
        self,
        player: Player,
        symbol: str,
        data: int,
    ) -> None:
        player.buy_stock(symbol, data)

    
    @post(
        operation_id="SellStock",
        path="/stock/{symbol:str}/sell",
    )
    async def sell_stock(
        self,
        player: Player,
        symbol: str,
        data: int,
    ) -> None:
        player.sell_stock(symbol, data)


    @post(
        operation_id="LiquidateStock",
        path="/stock/{symbol:str}/liquidate",
    )
    async def liquidate_stock(
        self,
        player: Player,
        symbol: str,
    ) -> None:
        player.liquidate_stock(symbol)
