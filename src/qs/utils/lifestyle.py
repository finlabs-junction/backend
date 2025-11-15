# Constants
HEALTH_BASE_DECAY = 2
SOCIAL_LIFE_BASE_DECAY = -10
STRESS_BASE_LEVEL = 10

FOOD_TYPE_HEALTH_BONUS = {
    'junk_food': -5,
    'basic_meal': 1,
    'healthy_meal': 5
}
HOUSING_QUALITY_HAPPINESS_BONUS = {
    'poor': -3,
    'average': 1,
    'luxury': 5
}
APARTMENT_TYPE_COMFORT_BONUS = {
    'low': 5,
    'mid': 15,
    'high': 25
}
LOCATION_TYPE_COMFORT_BONUS = {
    'suburbs': -5,
    'city_center': 30,
    'other': 0
}


class UserLifestyle:
    """
    A class to represent a user's lifestyle choices and habits.
    """

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

    def health(self, food_type: str, leisure_spent: int, current_month: int) -> int:
        """
        Calculate health based on food type consumed and base decay.
        """
        bonus = FOOD_TYPE_HEALTH_BONUS.get(food_type, 0)
        self.health += bonus - HEALTH_BASE_DECAY + leisure_spent // 50
        if current_month in [11, 12, 1, 2]:  # Winter months
            self.health -= 2  # Additional health decay in winter
        return self.health

    def happiness(self, leisure_spent: int, housing_quality: str, housing_has_sauna: bool, events: list[str]) -> int:
        """
        Calculate happiness based on leisure time, housing quality, and events.
        """
        bonus = HOUSING_QUALITY_HAPPINESS_BONUS.get(housing_quality, 0)
        sauna_bonus = 2 if housing_has_sauna else 0
        event_bonus = 10 if 'salary_bonus' in events else - \
            20 if 'job_loss' in events else 0

        self.happiness += (leisure_spent // 100) + \
            bonus + sauna_bonus + event_bonus
        return self.happiness

    def energy(self, work_hours_per_week: int, month: int) -> int:
        """
        Calculate energy based on work hours and seasonal effects.
        """
        health_loss = (100 - self.health) / 2
        work_loss = (work_hours_per_week - 40) * \
            2 if work_hours_per_week > 40 else -2

        if month in [6, 7, 8]:  # Summer months
            work_loss -= 10  # Less energy loss in summer

        if month in [11, 12, 1, 2]:  # Winter months
            health_loss += 20  # More energy loss in winter

        self.energy += - health_loss - work_loss

        return self.energy

    def social_life(self, leisure_budget: float, work_hours_per_week: float) -> int:
        """
        Calculate social life score based on leisure budget and work hours.

        Args:
            leisure_budget: Amount spent on leisure activities in EUR
            work_hours_per_week: Weekly work hours

        Returns:
            Updated social_life score
        """
        # Base decay
        change = SOCIAL_LIFE_BASE_DECAY

        # Leisure budget bonus: +5 for every 100 EUR spent (0 if under 100)
        if leisure_budget >= 100:
            change += 5 * (leisure_budget / 100)

        # Work hours bonus: +1 for every hour under 48h/week
        if work_hours_per_week < 48:
            change += (48 - work_hours_per_week)

        self.social_life += change
        return self.social_life

    def stress_level(
        self,
        savings: float,
        monthly_expenses: float,
        has_unsecured_debt: bool,
        crash_event_occurred: bool,
        stock_portfolio_change_pct: float,
        stock_exposure: float
    ) -> int:
        """
        Calculate stress level based on financial situation and events.

        Args:
            savings: Current savings amount
            monthly_expenses: Monthly expenses amount
            has_unsecured_debt: Whether user has unsecured debt (credit card)
            crash_event_occurred: Whether a market crash event occurred
            stock_portfolio_change_pct: Monthly percentage change in stock portfolio
            stock_exposure: Total stock portfolio exposure

        Returns:
            Updated stress_level score (capped at 80)
        """
        # Start with base level
        new_stress = STRESS_BASE_LEVEL

        # Savings to expenses ratio
        months_of_savings = savings / monthly_expenses if monthly_expenses > 0 else 0

        if months_of_savings < 1:
            new_stress += 20
        elif months_of_savings > 6:
            new_stress -= 10

        # Unsecured debt
        if has_unsecured_debt:
            new_stress += 10

        # Market crash event
        if crash_event_occurred:
            new_stress += 15

        # Stock portfolio impact
        if monthly_expenses > 0:
            portfolio_stress = (
                stock_exposure / monthly_expenses) * stock_portfolio_change_pct
            new_stress += portfolio_stress

        # Cap at 80
        self.stress_level = min(80, max(0, new_stress))
        return self.stress_level

    def living_comfort(
        self,
        apartment_type: str,
        private_living_space_m2: float,
        location_type: str
    ) -> int:
        """
        Calculate living comfort based on apartment characteristics.

        Args:
            apartment_type: Type of apartment ('low', 'mid', 'high')
            private_living_space_m2: Private living space in square meters
            location_type: Location type ('suburbs', 'city_center', 'other')

        Returns:
            Updated living_comfort score
        """
        comfort = 0

        # Private living space: +1 for every m² (capped at 50)
        comfort += min(50, private_living_space_m2)

        # Location bonus
        comfort += LOCATION_TYPE_COMFORT_BONUS.get(location_type, 0)

        # Apartment type bonus
        comfort += APARTMENT_TYPE_COMFORT_BONUS.get(apartment_type, 0)

        self.living_comfort = comfort
        return self.living_comfort

    def career_progress(
        self,
        months_employed: int,
        has_networking_events: bool,
        energy_variance: float = 0.0
    ) -> int:
        """
        Calculate career progress based on employment duration and activities.

        Args:
            months_employed: Number of months employed
            has_networking_events: Whether leisure budget includes networking events
            energy_variance: Random variance based on energy level (-1 to 1)

        Returns:
            Updated career_progress score
        """
        # Base growth: +1 per month employed
        self.career_progress += months_employed

        # Random variance based on energy
        self.career_progress += energy_variance

        # Networking events bonus
        if has_networking_events:
            self.career_progress += 5

        return self.career_progress

    def skills_education(self, days_invested_in_month: int) -> int:
        """
        Calculate skills and education level based on time investment.

        Args:
            days_invested_in_month: Number of days spent on self-improvement in the month

        Returns:
            Updated skills_education score
        """
        # Time investment: +1 for every day taken for self-improvement
        self.skills_education += days_invested_in_month

        return self.skills_education
