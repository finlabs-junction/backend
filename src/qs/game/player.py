from __future__ import annotations

import typing as t
from enum import StrEnum

from qs.exceptions import UnderflowError

if t.TYPE_CHECKING:
    from qs.game.session import Session


class Occupation(StrEnum):
    SOFTWARE_ENGINEER = "software_engineer"


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
        self._stocks: dict[str, int] = {
            symbol: 0
            for symbol in session.get_stock_prices().keys()
        }
        self._entry_prices: dict[str, float] = {
            symbol: 0.0
            for symbol in session.get_stock_prices().keys()
        }


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
        return 100
    

    def get_happiness_level(self) -> int:
        return 100
    

    def get_energy_level(self) -> int:
        return 100
    

    def get_social_life_level(self) -> int:
        return 100
    

    def get_stress_level(self) -> int:
        return 100
    

    def get_living_comfort_level(self) -> int:
        return 100
    

    def get_monthly_rent_expense(self) -> float:
        return 1000
    

    def get_monthly_utilities_expense(self) -> float:
        return 200
    

    def get_monthly_grocery_expense(self) -> float:
        return self._monthly_grocery_expense
    

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


    def tick(self) -> None:
        time = self._session.get_time()

        if time.day == 1 and time.hour == 0:
            self.receive_salary()
            self.pay_rent()
            self.pay_utilities()
            self.pay_loan_installment()
            self.pay_taxes()

        if time.hour in (6, 12, 18):
            self.buy_meal()

        if time.hour == 0:
            self.pay_daily_transportation()
            self.pay_daily_leisure()


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
