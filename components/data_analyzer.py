# Implements SRS FR-2.1 (Descriptive Statistics), FR-2.2 (Location Analysis),
#             FR-2.3 (Correlation Analysis)
"""
DataAnalyzer Component
-----------------------
Calculates statistical summaries, location-based price analysis, and
Pearson correlation analysis on the uploaded property dataset.
"""

import pandas as pd

# Column name constants — no magic strings
PRICE_COLUMN    = "Price"
LOCATION_COLUMN = "Location"

# Features to correlate with Price (Age is optional — used only if present in CSV)
NUMERIC_FEATURES = ["Area", "Bedrooms", "Bathrooms", "Age"]

# Number of decimal places for rounding results
ROUND_PLACES = 2
CORR_ROUND   = 4


class DataAnalyzer:
    """Performs statistical and correlation analysis on property data."""

    def __init__(self, dataframe):
        """
        Initialize with a Pandas DataFrame.

        Args:
            dataframe: Pandas DataFrame loaded from the uploaded CSV.
        """
        self.df = dataframe

    def calculate_statistics(self):
        """
        Calculate descriptive statistics for the Price column (SRS FR-2.1).

        Quartile explanation:
          Q1 = 25th percentile → bottom 25% of prices fall below this value
          Q3 = 75th percentile → top 25% of prices start above this value
          Together they show the "spread" of typical prices.

        Returns:
            Dict with keys: count, mean, median, std, min, max, q1, q3.
        """
        price = self.df[PRICE_COLUMN]
        return {
            "count":  int(price.count()),
            "mean":   round(float(price.mean()),             ROUND_PLACES),
            "median": round(float(price.median()),           ROUND_PLACES),
            "std":    round(float(price.std()),              ROUND_PLACES),
            "min":    round(float(price.min()),              ROUND_PLACES),
            "max":    round(float(price.max()),              ROUND_PLACES),
            "q1":     round(float(price.quantile(0.25)),     ROUND_PLACES),
            "q3":     round(float(price.quantile(0.75)),     ROUND_PLACES),
        }

    def location_analysis(self):
        """
        Group properties by Location and compute price stats per group (SRS FR-2.2).

        Steps:
          1. Group all rows by the Location column.
          2. For each group compute: average, min, max price and property count.
          3. Sort by average price (highest first) so top locations appear first.

        Returns:
            List of dicts sorted by avg_price descending.
            Each dict has: location, avg_price, min_price, max_price, count.
        """
        grouped = self.df.groupby(LOCATION_COLUMN).agg(
            avg_price=(PRICE_COLUMN, "mean"),
            min_price=(PRICE_COLUMN, "min"),
            max_price=(PRICE_COLUMN, "max"),
            count=(PRICE_COLUMN, "count"),
        ).reset_index()

        # Sort highest average price first
        grouped = grouped.sort_values("avg_price", ascending=False)

        result = []
        for _, row in grouped.iterrows():
            result.append({
                "location":  row[LOCATION_COLUMN],
                "avg_price": round(float(row["avg_price"]), ROUND_PLACES),
                "min_price": round(float(row["min_price"]), ROUND_PLACES),
                "max_price": round(float(row["max_price"]), ROUND_PLACES),
                "count":     int(row["count"]),
            })
        return result

    def correlation_analysis(self):
        """
        Calculate Pearson correlation between Price and numeric features (SRS FR-2.3).

        Correlation value guide:
          +0.7 to +1.0 → Strong positive (feature goes up, price goes up)
          +0.4 to +0.7 → Moderate positive
           0.0 to +0.4 → Weak or no relationship
          Negative values → inverse relationship (rare for these features)

        Only includes features that exist as columns in the CSV.
        Age is optional — skipped if not present.

        Returns:
            Dict mapping feature name → correlation value (4 decimal places).
            Example: {"Area": 0.8213, "Bedrooms": 0.6104, "Bathrooms": 0.5530}
        """
        correlations = {}
        for feature in NUMERIC_FEATURES:
            if feature in self.df.columns:
                corr_value = self.df[PRICE_COLUMN].corr(self.df[feature])
                correlations[feature] = round(float(corr_value), CORR_ROUND)
        return correlations
