from __future__ import annotations

import typing as t
from enum import StrEnum, Enum

if t.TYPE_CHECKING:
    from qs.game.session import Session


class Occupation(StrEnum):
    SOFTWARE_ENGINEER = "software_engineer"


class BaseDecays(Enum):
    HEALTH = -2
    HAPPINESS = -5
    SOCIAL_LIFE = -10
    CAREER = +1


class FOOD_TYPE(Enum):
    FAST_FOOD = {
        "health": -5,
        "cost": 100
    }
    HOME_COOKED = {
        "health": +1,
        "cost": 150
    }
    ORGANIC = {
        "health": +5,
        "cost": 250
    }


class HOUSING_QUALITY(Enum):
    LOW = {
        "happiness": -3,
        "comfort": -1,
        "cost": 800
    }
    MEDIUM = {
        "happiness": +1,
        "comfort": +15,
        "cost": 1500
    }
    HIGH = {
        "happiness": +5,
        "comfort": +25,
        "cost": 3000
    }


class LOCATION_TYPE(Enum):
    SUBURBS = {
        "comfort": -5,
        "cost": 1000
    }
    CITY_CENTER = {
        "comfort": +30,
        "cost": 2000
    }
    RURAL = {
        "comfort": -10,
        "cost": 500
    }


class UserLifestyle:
    def __init__(self, health: int, happiness: int, energy: int, social_life: int, stress_level: int,
                 living_comfort: int, career_progress: int, skills_education: int):
        self.health = health
        self.happiness = happiness
        self.energy = energy
        self.social_life = social_life
        self.stress_level = stress_level
        self.living_comfort = living_comfort
        self.career_progress = career_progress
        self.skills_education = skills_education

    def update_health(self, food_type: FOOD_TYPE, leisure_spent: int, current_month: int) -> int:
        bonus = food_type.value["health"]
        self.health += bonus + BaseDecays.HEALTH.value + leisure_spent // 50
        if current_month in [11, 12, 1, 2]:  # Winter months
            self.health -= 2  # Additional health decay in winter
        return self.health

    def update_happiness(self, leisure_spent: int, housing_quality: HOUSING_QUALITY, housing_has_sauna: bool, events: list[str]) -> int:
        bonus = housing_quality.value["happiness"]
        sauna_bonus = 2 if housing_has_sauna else 0
        event_bonus = 10 if 'salary_bonus' in events else -5
        self.happiness += bonus + sauna_bonus + event_bonus + \
            BaseDecays.HAPPINESS.value + leisure_spent // 30
        return self.happiness

    def update_energy(self, work_hours_per_week: int, month: int) -> int:
        health_loss = (100 - self.health) / 2
        work_loss = (work_hours_per_week - 40) * \
            2 if work_hours_per_week > 40 else -2
        seasonal_bonus = 5 if month in [
            6, 7, 8] else -5 if month in [11, 12, 1, 2] else 0
        self.energy += seasonal_bonus - health_loss - work_loss
        return self.energy

    def update_social_life(self, leisure_spent: int, work_hours_per_week: int) -> int:
        work_impact = (work_hours_per_week -
                       40) // 5 if work_hours_per_week > 40 else 0
        self.social_life += (leisure_spent // 100) + \
            BaseDecays.SOCIAL_LIFE.value - work_impact
        return self.social_life

    def update_stress_level(
        self,
        savings: int,
        monthly_expenses: int,
        unsecured_debt: int,
        crash_event_occurred: bool,
        stock_portfolio_performance: float,
        stock_exposure: float
    ) -> int:
        stress_change = 0
        if savings < monthly_expenses:
            stress_change += 20
        elif savings > monthly_expenses * 6:
            stress_change -= 10

        if unsecured_debt > 0:
            stress_change += unsecured_debt // 200

        if crash_event_occurred:
            stress_change += 15

        stress_change += int(-stock_portfolio_performance *
                             stock_exposure / monthly_expenses)

        self.stress_level += stress_change
        return self.stress_level

    def update_living_comfort(self, housing_quality: HOUSING_QUALITY, location_type: LOCATION_TYPE, private_living_space_m2: int) -> int:
        comfort_bonus = housing_quality.value["comfort"] + \
            location_type.value["comfort"] + private_living_space_m2
        self.living_comfort = comfort_bonus
        return self.living_comfort

    def update_career_progress(self, is_employed: bool, leisure_spent: int) -> int:
        if is_employed:
            self.career_progress += BaseDecays.CAREER.value + \
                (leisure_spent // 200)
        else:
            self.career_progress -= 2

        return self.career_progress

    def update_skills_education(self, education_hours_per_week: int) -> int:
        self.skills_education += education_hours_per_week // 2
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
        self._balance = 50000
        self._occupation = Occupation.SOFTWARE_ENGINEER
        self._monthly_grocery_expense = 300
        self._monthly_leisure_expense = 250
        self._food_type = FOOD_TYPE.HOME_COOKED
        self._housing_quality = HOUSING_QUALITY.MEDIUM
        self._location_type = LOCATION_TYPE.SUBURBS
        self._private_living_space_m2 = 50
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

    def get_session(self) -> Session:
        return self._session

    def get_username(self) -> str:
        return self._username

    def is_leader(self) -> bool:
        return self._is_leader

    def get_balance(self) -> float:
        return self._balance

    def get_monthly_income(self) -> float:
        return self.get_monthly_salary()

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
        return self._lifestyle.health

    def get_happiness_level(self) -> int:
        return self._lifestyle.happiness

    def get_energy_level(self) -> int:
        return self._lifestyle.energy

    def get_social_life_level(self) -> int:
        return self._lifestyle.social_life

    def get_stress_level(self) -> int:
        return self._lifestyle.stress_level

    def get_living_comfort_level(self) -> int:
        return self._lifestyle.living_comfort

    def get_career_progress_level(self) -> int:
        return self._lifestyle.career_progress

    def get_skills_education_level(self) -> int:
        return self._lifestyle.skills_education

    def get_monthly_rent_expense(self) -> float:
        return self._housing_quality.value["cost"] + self._location_type.value["cost"]

    def get_monthly_utilities_expense(self) -> float:
        return 200

    def get_monthly_grocery_expense(self) -> float:
        return self._food_type.value["cost"]

    def set_monthly_grocery_expense(self, amount: float) -> None:
        self._monthly_grocery_expense = amount

    def get_monthly_transportation_expense(self) -> float:
        return 150

    def get_monthly_leisure_expense(self) -> float:
        return self._monthly_leisure_expense

    def set_monthly_leisure_expense(self, amount: float) -> None:
        self._monthly_leisure_expense = amount

    def get_monthly_loan_expense(self) -> float:
        return 400

    def get_monthly_tax_expense(self) -> float:
        return 500

    def buy_meal(self) -> None:
        """Buy a meal. Players eat three times a day."""
        self._balance -= self.get_monthly_grocery_expense() * 4 / 365

    def pay_daily_transportation(self) -> None:
        """Pay for daily transportation."""
        self._balance -= self.get_monthly_transportation_expense() * 12 / 365

    def pay_daily_leisure(self) -> None:
        """Pay for daily leisure."""
        self._balance -= self.get_monthly_leisure_expense() * 12 / 365

    def pay_taxes(self) -> None:
        """Pay the monthly tax expense."""
        self._balance -= self.get_monthly_tax_expense()

    def pay_rent(self) -> None:
        """Pay the monthly rent expense."""
        self._balance -= self.get_monthly_rent_expense()

    def pay_utilities(self) -> None:
        """Pay the monthly utilities expense."""
        self._balance -= self.get_monthly_utilities_expense()

    def pay_loan_installment(self) -> None:
        """Pay the monthly loan installment."""
        self._balance -= self.get_monthly_loan_expense()

    def tick(self) -> None:
        time = self._session.get_time()

        if time.day == 1 and time.hour == 0:
            self._balance += self.get_monthly_salary()
            self._balance -= self.get_monthly_rent_expense()
            self._balance -= self.get_monthly_utilities_expense()
            self._balance -= self.get_monthly_loan_expense()
            self._balance -= self.get_monthly_tax_expense()

        if time.hour in (6, 12, 18):
            self.buy_meal()

        if time.hour == 0:
            self.pay_daily_transportation()
            self.pay_daily_leisure()

        if time.hour in (0, 6, 12, 18):
            self._lifestyle.update_health(
                food_type=self._food_type,
                leisure_spent=self.get_monthly_leisure_expense(),
                current_month=time.month
            )
            self._lifestyle.update_happiness(
                leisure_spent=self.get_monthly_leisure_expense() / 30,
                housing_quality=self._housing_quality,
                housing_has_sauna=False,
                events=[]
            )
            self._lifestyle.update_energy(
                work_hours_per_week=40,
                month=time.month
            )
            self._lifestyle.update_social_life(
                leisure_spent=self.get_monthly_leisure_expense() / 30,
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
                private_living_space_m2=self._private_living_space_m2
            )
            self._lifestyle.update_career_progress(
                is_employed=True,
                leisure_spent=self.get_monthly_leisure_expense() / 30
            )
            self._lifestyle.update_skills_education(
                education_hours_per_week=5
            )
