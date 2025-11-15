from __future__ import annotations

import typing as t
import secrets

from authlib.jose import jwt

from qs.contrib.litestar import *
from qs.events_data import get_event_by_id
from qs.nlp.chatbot import Chatbot
from qs.prompting import (
    EVENT_EXPLANATION_SYSTEM_PROMPT,
    EVENT_HINT_SYSTEM_PROMPT,
    TEXT_EXPLANATION_SYSTEM_PROMPT,
    build_event_prompt,
    build_text_explanation_prompt,
)
from qs.server import get_settings
from qs.server.exceptions import *
from qs.server.llm_client import call_llm
from qs.server.schemas import *
from qs.server.services import *
from qs.game.session import Session
from qs.game.player import Player, HOUSING_QUALITY, LOCATION_TYPE
from qs.server.dependencies import get_session


def get_routes() -> list[ControllerRouterHandler]:
    return [
        SessionController,
        GameController,
        LifestyleController,
        explain_event,
        explain_text
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
    ) -> SessionCreateResponse:
        session = await create_session()

        session.add_player(data.username, is_leader=True)

        token = create_token(
            session_id=session.get_id(),
            username=data.username,
        )

        return SessionCreateResponse(
            session_id=session.get_id(),
            token=token,  # Token returned in response body for client to use in Authorization header
        )

    @post(
        operation_id="SessionJoin",
        path="/{session_id:str}/join",
    )
    async def join(
        self,
        session: Session,
        data: SessionJoinRequest,
    ) -> SessionJoinResponse:
        session.add_player(data.username)

        token = create_token(
            session_id=session.get_id(),
            username=data.username,
        )

        return SessionJoinResponse(
            token=token,  # Token returned in response body for client to use in Authorization header
        )

    @get(
        operation_id="Logout",
        path="/logout",
    )
    async def logout(self) -> None:
        return None


class GameController(Controller):
    tags = ["Game"]
    signature_types = [Player]

    @post(
        operation_id="StartSession",
        path="/start",
    )
    async def start(
        self,
        leader: Player
    ) -> None:
        session = leader.get_session()
        session.start()

    @post(
        operation_id="PauseSession",
        path="/pause",
    )
    async def pause(
        self,
        leader: Player,
    ) -> None:
        session = leader.get_session()
        session.pause()

    @post(
        operation_id="StopSession",
        path="/stop",
    )
    async def stop(
        self,
        leader: Player,
    ) -> None:
        session = leader.get_session()
        session.stop()

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

        events = [
            EventResponse(
                id=event["id"],
                date=event["date"],
                title=event["title"],
                description=event["description"],
            ) for event in player.get_events()
        ]

        players = [
            PlayerStats(
                username=player.get_username(),
                balance=player.get_balance(),
            ) for player in session.get_players()
        ]

        return PollResponse(
            session_id=session.get_id(),
            session_status=session.get_status(),
            username=player.get_username(),
            is_leader=player.is_leader(),
            time=session.get_time(),
            time_progression_multiplier=session.get_time_progression_multiplier(),
            balance=player.get_balance(),
            assets=player.get_assets(),
            equity=player.get_equity(),
            monthly_income=player.get_monthly_income(),
            monthly_expenses=player.get_monthly_expenses(),
            monthly_net_income=player.get_monthly_net_income(),
            occupation=player.get_occupation().value,
            monthly_salary=player.get_monthly_salary(),
            monthly_dividends=player.get_monthly_dividends(),
            health_level=player.get_health_level(),
            happiness_level=player.get_happiness_level(),
            energy_level=player.get_energy_level(),
            social_life_level=player.get_social_life_level(),
            stress_level=player.get_stress_level(),
            living_comfort_level=player.get_living_comfort_level(),
            career_progress_level=player.get_career_progress_level(),
            skills_education_level=player.get_skills_education_level(),
            monthly_rent_expense=player.get_monthly_rent_expense(),
            monthly_utilities_expense=player.get_monthly_utilities_expense(),
            monthly_grocery_expense=player.get_monthly_grocery_expense(),
            monthly_transportation_expense=player.get_monthly_transportation_expense(),
            monthly_leisure_expense=player.get_monthly_leisure_expense(),
            monthly_loan_expense=player.get_monthly_loan_expense(),
            monthly_tax_expense=player.get_monthly_tax_expense(),
            stocks=stocks,
            events=events,
            players=players,
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
        player.set_monthly_food_budget(data)

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

    @get(
        operation_id="GetDividends",
        path="/dividends",
    )
    async def get_dividends(
        self,
        player: Player,
    ) -> dict[str, dict[date, float]]:
        session = player.get_session()
        return session.get_dividends()

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

    @get(
        operation_id="PlayerStateEvaluation",
        path="/evaluate-player-state",
        tags=["Explanations"],
    )
    async def evaluate_player_state(
        self,
        player: Player,
    ) -> ChatMessage:

        chatbot = Chatbot()
        evaluation = chatbot.evaluate_user_state(player)

        return ChatMessage(
            role="assistant",
            content=evaluation,
        )

    @post(
        operation_id="PlayerChat",
        path="/chat",
        tags=["Explanations"]
    )
    async def player_chat(
        self,
        player: Player,
        data: list[ChatMessage],
    ) -> ChatMessage:
        chatbot = Chatbot()
        response = chatbot.chat(player, data)
        return ChatMessage(
            role="assistant",
            content=response,
        )


class LifestyleController(Controller):
    path = "/lifestyle"
    tags = ["Lifestyle"]
    signature_types = [Player]

    @get(
        operation_id="ListAccommodations",
        path="/accommodations",
    )
    async def list_accommodations(
        self,
        player: Player,
    ) -> ListAccommodationsResponse:
        """List all available accommodation options."""
        current_details = player.get_accommodation_details()

        accommodations = []

        # Generate accommodation options based on combinations of quality, location, and size
        sizes = [30, 50, 70, 100]

        for quality in HOUSING_QUALITY:
            for location in LOCATION_TYPE:
                for sqm in sizes:
                    # Calculate rent and utilities
                    monthly_rent = quality.value["cost"] + \
                        location.value["cost"]
                    monthly_utilities = 100 + (sqm * 2)

                    accommodation_id = f"{quality.name.lower()}_{location.name.lower()}_{sqm}"

                    # Create description
                    quality_desc = {
                        "LOW": "Basic",
                        "MEDIUM": "Standard",
                        "HIGH": "Luxury"
                    }[quality.name]

                    location_desc = {
                        "SUBURBS": "Suburban area",
                        "CITY_CENTER": "City center",
                        "RURAL": "Rural area"
                    }[location.name]

                    description = f"{quality_desc} accommodation in {location_desc}, {sqm}m²"

                    accommodations.append(
                        AccommodationOption(
                            id=accommodation_id,
                            name=f"{quality_desc} - {location_desc} ({sqm}m²)",
                            quality=quality.name,
                            location=location.name,
                            sqm=sqm,
                            monthly_rent=monthly_rent,
                            monthly_utilities=monthly_utilities,
                            description=description,
                        )
                    )

        return ListAccommodationsResponse(
            current_accommodation_id=current_details["id"],
            accommodations=accommodations,
        )

    @post(
        operation_id="MoveAccommodation",
        path="/accommodations/move",
    )
    async def move_accommodation(
        self,
        player: Player,
        data: MoveAccommodationRequest,
    ) -> None:
        """Move to a new accommodation."""
        # Parse accommodation_id to extract quality, location, and sqm
        # Format: quality_location_sqm (e.g., "medium_city_center_70")
        parts = data.accommodation_id.split("_")

        if len(parts) < 3:
            raise BadRequestError("Invalid accommodation ID format")

        # Handle location names with underscores (e.g., city_center)
        if len(parts) == 4:
            quality_str = parts[0].upper()
            location_str = f"{parts[1]}_{parts[2]}".upper()
            sqm = float(parts[3])
        else:
            quality_str = parts[0].upper()
            location_str = parts[1].upper()
            sqm = float(parts[2])

        # Validate and get enums
        try:
            quality = HOUSING_QUALITY[quality_str]
            location = LOCATION_TYPE[location_str]
        except KeyError:
            raise BadRequestError(
                "Invalid quality or location in accommodation ID")

        # Move to new accommodation
        player.move_accommodation(
            accommodation_id=data.accommodation_id,
            quality=quality,
            location=location,
            sqm=sqm,
        )


@post(
    operation_id="ExplainEvent",
    path="/events/{event_id:int}/explanation",
    tags=["Explanations"],
)
async def explain_event(
    event_id: int
) -> ExplanationResponse:
    event = get_event_by_id(event_id)
    if event is None:
        raise NotFoundError("Event not found")

    prompt = build_event_prompt(event)
    explanation = call_llm(EVENT_EXPLANATION_SYSTEM_PROMPT, prompt)
    hint = call_llm(EVENT_HINT_SYSTEM_PROMPT, prompt)

    return ExplanationResponse(explanation=explanation, hint=hint)


@post(
    operation_id="ExplainText",
    path="/explain-text",
    tags=["Explanations"],
)
async def explain_text(
    data: TextExplanationRequest
) -> ExplanationResponse:
    prompt = build_text_explanation_prompt(data.text, data.context)
    text = call_llm(TEXT_EXPLANATION_SYSTEM_PROMPT, prompt)

    return ExplanationResponse(explanation=text)
