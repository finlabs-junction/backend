from __future__ import annotations

from qs.contrib.msgspec import *
from qs.game.session import SessionStatus


class SessionCreateRequest(Struct):
    username: str


class SessionCreateResponse(Struct):
    session_id: str


class SessionJoinRequest(Struct):
    username: str


class PollResponse(Struct):
    session_id: str
    session_status: SessionStatus
    username: str
    is_leader: bool
    time: datetime
    time_progression_multiplier: int

    balance: float
    monthly_income: float
    monthly_expenses: float
    monthly_net_income: float
    occupation: str
    monthly_salary: float
    health_level: int
    happiness_level: int
    energy_level: int
    social_life_level: int
    stress_level: int
    living_comfort_level: int
    monthly_rent_expense: float
    monthly_utilities_expense: float
    monthly_grocery_expense: float
    monthly_transportation_expense: float
    monthly_leisure_expense: float
    monthly_loan_expense: float
    monthly_tax_expense: float
    stocks: list[Position]


class Position(Struct):
    symbol: str
    size: int
    last_price: float
    entry_price: float
    pnl: float
