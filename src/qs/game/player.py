from __future__ import annotations

import typing as t
from enum import StrEnum, Enum
from datetime import timedelta

from qs.events_data import EVENTS_DF
from qs.exceptions import UnderflowError
from qs.game.priceMultiplier import PriceMultiplier

if t.TYPE_CHECKING:
    from qs.game.session import Session


class Occupation(StrEnum):
    SOFTWARE_ENGINEER = "software_engineer"


class BaseDecays(Enum):
    HEALTH = -0.25
    HAPPINESS = -5 / 8
    SOCIAL_LIFE = -1
    CAREER = +0.02


class FOOD_TYPE(Enum):
    FAST_FOOD = {
        "health": -2,
        "cost": 100
    }
    HOME_COOKED = {
        "health": +.1,
        "cost": 150
    }
    ORGANIC = {
        "health": +1,
        "cost": 250
    }


class HOUSING_QUALITY(Enum):
    LOW = {
        "happiness": -3/4,
        "comfort": -1/4,
        "cost": 800
    }
    MEDIUM = {
        "happiness": +1/4,
        "comfort": +15/4,
        "cost": 1500
    }
    HIGH = {
        "happiness": +5/4,
        "comfort": +25/4,
        "cost": 3000
    }


class LOCATION_TYPE(Enum):
    SUBURBS = {
        "comfort": -5/4,
        "cost": 1000
    }
    CITY_CENTER = {
        "comfort": +30/4,
        "cost": 2000
    }
    RURAL = {
        "comfort": -10/4,
        "cost": 500
    }


class UserLifestyle:
    def __init__(
        self,
        health: float,
        happiness: float,
        energy: float,
        social_life: float,
        stress_level: float,
        living_comfort: float,
        career_progress: float,
        skills_education: float,
    ):
        self.health = health
        self.happiness = happiness
        self.energy = energy
        self.social_life = social_life
        self.stress_level = stress_level
        self.living_comfort = living_comfort
        self.career_progress = career_progress
        self.skills_education = skills_education

    def update_health(
        self,
        food_type: FOOD_TYPE,
        leisure_spent: float,
        current_month: float,
    ) -> float:
        bonus = food_type.value["health"]
        self.health += bonus + BaseDecays.HEALTH.value + leisure_spent / 50
        if current_month in [11, 12, 1, 2]:  # Winter months
            self.health -= 2  # Additional health decay in winter

        if self.health < 0:
            self.health = 0
        elif self.health > 100:
            self.health = 100

        return self.health

    def update_happiness(
        self,
        leisure_spent: float,
        housing_quality: HOUSING_QUALITY,
        housing_has_sauna: bool,
        events: list[str],
    ) -> float:
        bonus = housing_quality.value["happiness"]
        sauna_bonus = 2 if housing_has_sauna else 0
        event_bonus = 10 if 'salary_bonus' in events else 0
        self.happiness += bonus + sauna_bonus + event_bonus + \
            BaseDecays.HAPPINESS.value + leisure_spent / 10

        if self.happiness < 0:
            self.happiness = 0
        elif self.happiness > 100:
            self.happiness = 100

        return self.happiness

    def update_energy(self, work_hours_per_week: int, month: int) -> float:
        health_loss = (100 - self.health) / 2
        work_loss = (work_hours_per_week - 40) * \
            2 if work_hours_per_week > 40 else -2
        seasonal_bonus = .1 if month in [
            6, 7, 8] else -.1 if month in [11, 12, 1, 2] else 0
        self.energy += seasonal_bonus - health_loss - work_loss

        if self.energy < 0:
            self.energy = 0
        elif self.energy > 100:
            self.energy = 100

        return self.energy

    def update_social_life(
        self,
        leisure_spent: float,
        work_hours_per_week: int,
    ) -> float:
        work_impact = (work_hours_per_week -
                       40) / 5 if work_hours_per_week > 40 else -2
        self.social_life += (leisure_spent / 100) + \
            BaseDecays.SOCIAL_LIFE.value - work_impact

        if self.social_life < 0:
            self.social_life = 0
        elif self.social_life > 100:
            self.social_life = 100

        return self.social_life

    def update_stress_level(
        self,
        savings: float,
        monthly_expenses: float,
        unsecured_debt: float,
        crash_event_occurred: bool,
        stock_portfolio_performance: float,
        stock_exposure: float
    ) -> float:
        stress_change = 0
        if savings < monthly_expenses:
            stress_change += 20
        elif savings > monthly_expenses * 6:
            stress_change -= 10

        if unsecured_debt > 0:
            stress_change += unsecured_debt / 200

        if crash_event_occurred:
            stress_change += 15

        stress_change += int(-stock_portfolio_performance *
                             stock_exposure / monthly_expenses)

        self.stress_level += stress_change

        if self.stress_level < 0:
            self.stress_level = 0
        elif self.stress_level > 100:
            self.stress_level = 100

        return self.stress_level

    def update_living_comfort(
        self,
        housing_quality: HOUSING_QUALITY,
        location_type: LOCATION_TYPE,
        private_living_space_sqm: float,
    ) -> float:
        comfort_bonus = housing_quality.value["comfort"] + \
            location_type.value["comfort"] + private_living_space_sqm
        self.living_comfort = comfort_bonus

        if self.living_comfort < 0:
            self.living_comfort = 0
        elif self.living_comfort > 100:
            self.living_comfort = 100

        return self.living_comfort

    def update_career_progress(
        self,
        is_employed: bool,
        leisure_spent: float,
    ) -> float:
        if is_employed:
            self.career_progress += BaseDecays.CAREER.value + \
                (leisure_spent / 2000)
        else:
            self.career_progress -= 2

        if self.career_progress < 0:
            self.career_progress = 0
        elif self.career_progress > 100:
            self.career_progress = 100

        return self.career_progress

    def update_skills_education(self, education_hours_per_week: int) -> float:
        self.skills_education += education_hours_per_week / 24

        if self.skills_education < 0:
            self.skills_education = 0
        elif self.skills_education > 100:
            self.skills_education = 100

        return self.skills_education


SALARIES = {
    Occupation.SOFTWARE_ENGINEER: 5000,
}


def get_monthly_salary(occupation: Occupation) -> int:
    return SALARIES[occupation]


class Player:
    def __init__(
        self,
        session: Session,
        username: str,
        is_leader: bool = False,
    ):
        self._session = session
        self._username = username
        self._is_leader = is_leader
        self._balance = 50000.0
        self._occupation = Occupation.SOFTWARE_ENGINEER
        self._monthly_grocery_expense = 300.0
        self._monthly_leisure_expense = 250.0
        self._stocks: dict[str, int] = {
            symbol: 0
            for symbol in session.get_stock_prices().keys()
        }
        self._entry_prices: dict[str, float] = {
            symbol: 0.0
            for symbol in session.get_stock_prices().keys()
        }

        self._food_type = FOOD_TYPE.HOME_COOKED
        self._housing_quality = HOUSING_QUALITY.MEDIUM
        self._location_type = LOCATION_TYPE.SUBURBS
        self._private_living_space_sqm = 50
        self._accommodation_id = "default_medium_suburbs_50"
        self._lifestyle = UserLifestyle(
            health=100,
            happiness=100,
            energy=100,
            social_life=100,
            stress_level=0,
            living_comfort=50,
            career_progress=0,
            skills_education=0,
        )
        self._events = []
        self._priceMultiplier = PriceMultiplier()
        self._multiplier = 1

    def get_session(self) -> Session:
        return self._session

    def get_events(self) -> list[dict]:
        return self._events

    def get_username(self) -> str:
        return self._username

    def is_leader(self) -> bool:
        return self._is_leader

    def get_balance(self) -> float:
        return self._balance

    def get_assets(self) -> float:
        assets = self.get_stock_portfolio_value()

        if self._balance > 0:
            assets += self._balance

        return assets

    def get_stock_portfolio_value(self) -> float:
        return sum(
            self._session.get_stock_price(symbol) * size
            for symbol, size in self._stocks.items()
        )

    def get_equity(self) -> float:
        stocks = self.get_stock_portfolio_value()
        return self._balance + stocks

    def get_monthly_income(self) -> float:
        return self.get_monthly_salary() + self.get_monthly_dividends()

    def get_monthly_expenses(self) -> float:
        return (
            self.get_monthly_rent_expense() +
            self.get_monthly_utilities_expense() +
            self.get_monthly_grocery_expense() +
            self.get_monthly_transportation_expense() +
            self.get_monthly_leisure_expense() +
            self.get_monthly_loan_expense() +
            self.get_monthly_tax_expense()
        )

    def get_monthly_net_income(self) -> float:
        return self.get_monthly_income() - self.get_monthly_expenses()

    def get_occupation(self) -> Occupation:
        return self._occupation

    def get_monthly_salary(self) -> float:
        return get_monthly_salary(self._occupation)

    def get_health_level(self) -> int:
        return round(self._lifestyle.health)

    def get_happiness_level(self) -> int:
        return round(self._lifestyle.happiness)

    def get_energy_level(self) -> int:
        return round(self._lifestyle.energy)

    def get_social_life_level(self) -> int:
        return round(self._lifestyle.social_life)

    def get_stress_level(self) -> int:
        return round(self._lifestyle.stress_level)

    def get_living_comfort_level(self) -> int:
        return round(self._lifestyle.living_comfort)

    def get_career_progress_level(self) -> int:
        return round(self._lifestyle.career_progress)

    def get_skills_education_level(self) -> int:
        return round(self._lifestyle.skills_education)

    def get_monthly_rent_expense(self) -> float:
        return (self._housing_quality.value["cost"] + self._location_type.value["cost"]) * self._multiplier

    def get_monthly_utilities_expense(self) -> float:
        # Base utilities of 100, plus 2 per sqm
        return (100 + (self._private_living_space_sqm * 2)) * self._multiplier

    def get_monthly_grocery_expense(self) -> float:
        return self._food_type.value["cost"]

    def set_monthly_grocery_expense(self, amount: float) -> None:
        self._monthly_grocery_expense = amount

    def get_monthly_transportation_expense(self) -> float:
        return 150 * self._multiplier

    def get_monthly_leisure_expense(self) -> float:
        return self._monthly_leisure_expense

    def set_monthly_leisure_expense(self, amount: float) -> None:
        self._monthly_leisure_expense = amount

    def set_monthly_food_budget(self, amount: float) -> None:
        """Set the monthly food budget and adjust food type accordingly."""
        self._monthly_grocery_expense = amount

        # Adjust food type based on budget
        if amount / self._multiplier >= 250:
            self._food_type = FOOD_TYPE.ORGANIC
        elif amount / self._multiplier >= 150:
            self._food_type = FOOD_TYPE.HOME_COOKED
        else:
            self._food_type = FOOD_TYPE.FAST_FOOD

    def get_accommodation_id(self) -> str:
        """Get the current accommodation ID."""
        return self._accommodation_id

    def get_accommodation_details(self) -> dict:
        """Get details about current accommodation."""
        return {
            "id": self._accommodation_id,
            "quality": self._housing_quality.name,
            "location": self._location_type.name,
            "sqm": self._private_living_space_sqm,
            "monthly_rent": self.get_monthly_rent_expense(),
            "monthly_utilities": self.get_monthly_utilities_expense(),
        }

    def move_accommodation(
        self,
        accommodation_id: str,
        quality: HOUSING_QUALITY,
        location: LOCATION_TYPE,
        sqm: float,
    ) -> None:
        """Move to a new accommodation."""
        self._accommodation_id = accommodation_id
        self._housing_quality = quality
        self._location_type = location
        self._private_living_space_sqm = sqm

    def get_monthly_loan_expense(self) -> float:
        return 400

    def get_monthly_tax_expense(self) -> float:
        return 500

    def credit(self, amount: float) -> None:
        """Credit the player's balance."""
        self._balance += amount

    def debit(self, amount: float) -> None:
        """Debit the player's balance."""
        self._balance -= amount

    def receive_salary(self) -> None:
        """Receive the monthly salary."""
        self.credit(self.get_monthly_salary())

    def buy_meal(self) -> None:
        """Buy a meal. Players eat three times a day."""
        expense = self.get_monthly_grocery_expense() * 4 / 365
        self.debit(expense)

    def pay_daily_transportation(self) -> None:
        """Pay for daily transportation."""
        expense = self.get_monthly_transportation_expense() * 12 / 365
        self.debit(expense)

    def pay_daily_leisure(self) -> None:
        """Pay for daily leisure."""
        expense = self.get_monthly_leisure_expense() * 12 / 365
        self.debit(expense)

    def pay_taxes(self) -> None:
        """Pay the monthly tax expense."""
        self.debit(self.get_monthly_tax_expense())

    def pay_rent(self) -> None:
        """Pay the monthly rent expense."""
        self.debit(self.get_monthly_rent_expense())

    def pay_utilities(self) -> None:
        """Pay the monthly utilities expense."""
        self.debit(self.get_monthly_utilities_expense())

    def pay_loan_installment(self) -> None:
        """Pay the monthly loan installment."""
        self.debit(self.get_monthly_loan_expense())

    def get_events_for_date(self) -> None:
        session_time = self._session.get_time()

        """Retrieve events for a specific date."""
        events = EVENTS_DF[EVENTS_DF['Date'] ==
                           f"{session_time.month:02d}-{session_time.day:02d}-{session_time.year:04d}"]

        if not events.empty:
            self._events = [
                {
                    "id": row['ID'],
                    "date": row['Date'],
                    "title": row['Event Title'],
                    "description": row['Description']
                }
                for _, row in events.iterrows()
            ]
        else:
            self._events = []

    def tick(self) -> None:
        time = self._session.get_time()

        self.get_events_for_date()

        self._multiplier = self._priceMultiplier.multiplier_for_month(
            time.year, time.month)

        if time.hour == 0:
            if self.get_balance() < 0:
                # on a negative balance, incur daily interest 40% APR
                interest = -self.get_balance() * (0.4 / 365)
                self.debit(interest)

            self.pay_daily_transportation()
            self.pay_daily_leisure()
            self.receive_dividends()

        if time.day == 1 and time.hour == 0:
            self.receive_salary()
            self.pay_rent()
            self.pay_utilities()
            self.pay_loan_installment()
            self.pay_taxes()

        if time.hour in (6, 12, 18):
            self.buy_meal()

        if time.hour in (0, 6, 12, 18):
            self._lifestyle.update_health(
                food_type=self._food_type,
                leisure_spent=self.get_monthly_leisure_expense() / self._multiplier,
                current_month=time.month
            )
            self._lifestyle.update_happiness(
                leisure_spent=self.get_monthly_leisure_expense() / self._multiplier / 30,
                housing_quality=self._housing_quality,
                housing_has_sauna=False,
                events=[]
            )
            self._lifestyle.update_energy(
                work_hours_per_week=32,
                month=time.month
            )
            self._lifestyle.update_social_life(
                leisure_spent=self.get_monthly_leisure_expense() / self._multiplier / 30,
                work_hours_per_week=40
            )
            self._lifestyle.update_stress_level(
                savings=self._balance,
                monthly_expenses=self.get_monthly_expenses(),
                unsecured_debt=0,
                crash_event_occurred=False,
                stock_portfolio_performance=0.0,
                stock_exposure=0.0
            )
            self._lifestyle.update_living_comfort(
                housing_quality=self._housing_quality,
                location_type=self._location_type,
                private_living_space_sqm=self._private_living_space_sqm
            )
            self._lifestyle.update_career_progress(
                is_employed=True,
                leisure_spent=self.get_monthly_leisure_expense() / self._multiplier / 30
            )
            self._lifestyle.update_skills_education(
                education_hours_per_week=2
            )

    def get_position_size(self, symbol: str) -> int:
        return self._stocks.get(symbol, 0)

    def get_position_entry_price(self, symbol: str) -> float:
        return self._entry_prices.get(symbol, 0.0)

    def get_position_pnl(self, symbol: str) -> float:
        entry_price = self.get_position_entry_price(symbol)
        current_price = self._session.get_stock_price(symbol)
        size = self.get_position_size(symbol)
        return (current_price - entry_price) * size

    def buy_stock(self, symbol: str, quantity: int) -> None:
        last_price = self._session.get_stock_price(symbol)
        expense = last_price * quantity

        size_before = self._stocks[symbol]
        size_after = size_before + quantity

        entry_price_before = self._entry_prices[symbol]
        entry_price_after = (
            (entry_price_before * size_before) +
            (last_price * quantity)
        ) / size_after

        self.debit(expense)
        self._stocks[symbol] += quantity
        self._entry_prices[symbol] = entry_price_after

    def sell_stock(self, symbol: str, quantity: int) -> None:
        size_before = self._stocks.get(symbol, 0)
        size_after = size_before - quantity

        if size_after < 0:
            raise UnderflowError(
                symbol=symbol,
                attempted_reduction=quantity,
                current_size=size_before,
            )

        last_price = self._session.get_stock_price(symbol)
        revenue = last_price * quantity

        entry_price_before = self._entry_prices[symbol]
        entry_price_after = (
            (entry_price_before * size_before) -
            (entry_price_before * quantity)
        ) / size_after if size_after > 0 else 0.0

        self.credit(revenue)
        self._stocks[symbol] -= quantity
        self._entry_prices[symbol] = entry_price_after

    def liquidate_stock(self, symbol: str) -> None:
        size = self._stocks.get(symbol, 0)
        price = self._session.get_stock_price(symbol)
        revenue = price * size
        self.credit(revenue)
        self._stocks[symbol] = 0
        self._entry_prices[symbol] = 0.0

    def get_monthly_dividends(self) -> float:
        dividends_data = self._session.get_dividends()
        current_date = self._session.get_time().date()
        total_dividends = 0.0

        for symbol, size in self._stocks.items():
            daily_dividends = dividends_data.get(symbol, {})
            it = current_date - timedelta(days=29)
            while it <= current_date:
                dividend_per_share = daily_dividends.get(it, 0.0)
                total_dividends += dividend_per_share * size
                it += timedelta(days=1)

        return total_dividends

    def get_dividends(self) -> float:
        dividends_data = self._session.get_dividends()
        current_date = self._session.get_time().date()
        total_dividends = 0.0

        for symbol, size in self._stocks.items():
            daily_dividends = dividends_data.get(symbol, {})
            dividend_per_share = daily_dividends.get(current_date, 0.0)
            total_dividends += dividend_per_share * size

        return total_dividends

    def receive_dividends(self) -> None:
        dividends = self.get_dividends()
        self.credit(dividends)

    def dump_player_data(self) -> dict:
        return {
            "username": self._username,
            "is_leader": self._is_leader,
            "balance": self._balance,
            "occupation": self._occupation.value,
            "monthly_grocery_expense": self._monthly_grocery_expense,
            "monthly_leisure_expense": self._monthly_leisure_expense,
            "stocks": self._stocks,
            "entry_prices": self._entry_prices,
            "food_type": self._food_type.name,
            "housing_quality": self._housing_quality.name,
            "location_type": self._location_type.name,
            "private_living_space_sqm": self._private_living_space_sqm,
            "accommodation_id": self._accommodation_id,
            "lifestyle": {
                "health": self._lifestyle.health,
                "happiness": self._lifestyle.happiness,
                "energy": self._lifestyle.energy,
                "social_life": self._lifestyle.social_life,
                "stress_level": self._lifestyle.stress_level,
                "living_comfort": self._lifestyle.living_comfort,
                "career_progress": self._lifestyle.career_progress,
                "skills_education": self._lifestyle.skills_education,
            },
        }
