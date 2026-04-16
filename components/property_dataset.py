# Implements SRS FR-1.2 (Data Validation), FR-1.3 (Data Preview)
"""
PropertyDataset Component
--------------------------
Loads a CSV file into a Pandas DataFrame and validates its structure
and content against the rules defined in SRS FR-1.2.
"""

import pandas as pd

# Required columns per SRS FR-1.2
REQUIRED_COLUMNS = ["Location", "Price", "Area", "Bedrooms", "Bathrooms"]

# Value range constants per SRS FR-1.2
MIN_RECORDS = 100
MIN_AREA = 100
MAX_AREA = 10000
MIN_BEDROOMS = 1
MAX_BEDROOMS = 10
MIN_BATHROOMS = 1
MAX_BATHROOMS = 8


class PropertyDataset:
    """Loads CSV data and validates its structure and content."""

    def __init__(self):
        """Initialize with an empty dataset."""
        self.filename = ""
        self.dataframe = None   # Will hold the Pandas DataFrame after load
        self.record_count = 0

    def load_csv(self, filepath):
        """
        Load a CSV file into a Pandas DataFrame.

        Pandas explanation: Pandas reads the CSV file into a "DataFrame",
        which is like an in-memory spreadsheet with rows and columns.

        Args:
            filepath: Full path to the CSV file.

        Returns:
            True if loaded successfully, False if file is unreadable.
        """
        try:
            self.dataframe = pd.read_csv(filepath)
            self.record_count = len(self.dataframe)
            return True
        except Exception:
            return False

    def validate_data(self):
        """
        Validate the loaded DataFrame against SRS FR-1.2 rules.

        Checks performed:
        1. All required columns must be present.
        2. Minimum 100 records must exist.
        3. Price column must be > 0 for all rows.
        4. Area column must be between 100 and 10000 sq ft.

        Returns:
            (True, []) if all checks pass.
            (False, [list of error strings]) if any check fails.
        """
        errors = []

        if self.dataframe is None:
            return False, ["Dataset is not loaded."]

        # Check 1: Required columns
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in self.dataframe.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")

        # Check 2: Minimum record count
        if self.record_count < MIN_RECORDS:
            errors.append(
                f"Dataset must have at least {MIN_RECORDS} records. Found: {self.record_count}."
            )

        # Checks 3 and 4 only run when required columns are confirmed present
        if not missing_cols:
            if (self.dataframe["Price"] <= 0).any():
                errors.append("All Price values must be greater than 0.")

            area_out = (
                (self.dataframe["Area"] < MIN_AREA) |
                (self.dataframe["Area"] > MAX_AREA)
            )
            if area_out.any():
                errors.append(
                    f"Area values must be between {MIN_AREA} and {MAX_AREA} sq ft."
                )

        if errors:
            return False, errors
        return True, []

    def get_preview(self, rows=20):
        """
        Return the first N rows of the dataset as a list of dictionaries.

        Returns a list of dicts so the HTML template can loop over rows easily.
        Example: [{"Location": "Lahore", "Price": 15000000, ...}, ...]

        Args:
            rows: Number of rows to return (default 20 per SRS FR-1.3).

        Returns:
            List of row dicts, or empty list if no data is loaded.
        """
        if self.dataframe is None:
            return []
        return self.dataframe.head(rows).to_dict(orient="records")

    def get_statistics(self):
        """
        Calculate basic statistics for the Price column.

        Returns:
            Dict with keys: count, mean, median, std, min, max.
            Returns empty dict if no data is loaded.
        """
        if self.dataframe is None:
            return {}
        price = self.dataframe["Price"]
        return {
            "count": int(price.count()),
            "mean":   round(float(price.mean()), 2),
            "median": round(float(price.median()), 2),
            "std":    round(float(price.std()), 2),
            "min":    round(float(price.min()), 2),
            "max":    round(float(price.max()), 2),
        }
