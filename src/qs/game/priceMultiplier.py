import pandas as pd
from pathlib import Path


class PriceMultiplier:
    def __init__(self):
        # Get the path to the CSV file
        csv_path = Path(__file__).parent.parent / \
            'resources' / 'finland_cost_of_living.csv'
        self.df = pd.read_csv(csv_path)
        # Use the first entry as base value
        self.base_value = self.df['Point figure'].iloc[0]
        self.multiplier = 1

    def multiplier_for_month(self, year: int, month: int) -> float:
        """
        Calculate price multiplier for a given month and year based on cost of living data.

        Args:
            year: The year (e.g., 2005)
            month: The month (1-12)

        Returns:
            float: Price multiplier (1.0 = base value, >1.0 = more expensive, <1.0 = cheaper)
        """
        # Format the month string to match CSV format (e.g., "2005M01")
        month_str = f"{year}M{month:02d}"

        # Find the row matching the given month
        row = self.df[self.df['Month'] == month_str]

        if row.empty:
            raise ValueError(f"No data found for {year}-{month:02d}")

        # Get the point figure for this month
        point_figure = row['Point figure'].iloc[0]

        # Calculate multiplier: ratio of current value to base value
        multiplier = point_figure / self.base_value

        return multiplier
