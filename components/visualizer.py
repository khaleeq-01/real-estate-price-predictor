# Implements SRS FR-3.1 (Bar Chart), FR-3.2 (Scatter Plot), FR-3.3 (Pie Chart)
"""
Visualizer Component
---------------------
Generates Chart.js-compatible JSON data structures for the three dashboard charts.

Chart.js data format:
  Every chart needs a dict with "labels" and "datasets".
  The datasets list contains one or more series, each with a "data" list.
  For scatter charts, each data point is {"x": value, "y": value}.
"""

# Column name constants
PRICE_COLUMN         = "Price"
LOCATION_COLUMN      = "Location"
AREA_COLUMN          = "Area"
PROPERTY_TYPE_COLUMN = "PropertyType"

# How many top locations to show in the bar chart (SRS FR-3.1)
TOP_N_LOCATIONS = 10

# Cap scatter plot points for chart performance (large CSVs stay snappy)
MAX_SCATTER_POINTS = 500

# Colour palette — consistent with site's dark-blue theme + accents
BAR_BACKGROUND  = "rgba(44, 62, 80, 0.8)"
BAR_BORDER      = "rgba(44, 62, 80, 1.0)"
SCATTER_COLOR   = "rgba(52, 152, 219, 0.55)"

# Pie chart colours — one per property type
PIE_COLORS = [
    "#2c3e50", "#3498db", "#2ecc71", "#e74c3c",
    "#f39c12", "#9b59b6", "#1abc9c", "#e67e22",
    "#34495e", "#16a085",
]


class Visualizer:
    """Generates Chart.js-compatible chart data for the dashboard page."""

    def __init__(self, dataframe):
        """
        Initialize with a Pandas DataFrame.

        Args:
            dataframe: Pandas DataFrame loaded from the uploaded CSV.
        """
        self.df = dataframe

    def generate_bar_chart(self):
        """
        Build Chart.js data for top 10 locations by average price (SRS FR-3.1).

        Steps:
          1. Group by Location, calculate mean Price per location.
          2. Sort descending, take top 10.
          3. Return Chart.js bar-chart dict.

        Returns:
            Dict with 'labels' (location names) and 'datasets' (avg prices).
        """
        top_locations = (
            self.df.groupby(LOCATION_COLUMN)[PRICE_COLUMN]
            .mean()
            .sort_values(ascending=False)
            .head(TOP_N_LOCATIONS)
        )

        return {
            "labels": list(top_locations.index),
            "datasets": [{
                "label":           "Average Price (PKR)",
                "data":            [round(float(v), 2) for v in top_locations.values],
                "backgroundColor": BAR_BACKGROUND,
                "borderColor":     BAR_BORDER,
                "borderWidth":     1,
            }],
        }

    def generate_scatter_plot(self):
        """
        Build Chart.js scatter data for Price vs Area (SRS FR-3.2).

        Chart.js scatter format requires each point as {"x": ..., "y": ...}.
        x = Area (sq ft), y = Price (PKR).

        Capped at MAX_SCATTER_POINTS rows so the browser stays responsive.

        Returns:
            Dict with 'datasets' containing a list of {x, y} point dicts.
        """
        # Take only the two needed columns, capped for performance
        sample = self.df[[AREA_COLUMN, PRICE_COLUMN]].head(MAX_SCATTER_POINTS)

        # Rename columns to x/y — Chart.js scatter format requires these keys
        points = (
            sample
            .rename(columns={AREA_COLUMN: "x", PRICE_COLUMN: "y"})
            .to_dict(orient="records")
        )

        return {
            "datasets": [{
                "label":           "Price vs Area",
                "data":            points,
                "backgroundColor": SCATTER_COLOR,
                "pointRadius":     4,
                "pointHoverRadius": 6,
            }],
        }

    def generate_pie_chart(self):
        """
        Build Chart.js pie data for property type distribution (SRS FR-3.3).

        Uses the 'PropertyType' column if it exists in the CSV.
        If the column is absent, returns a placeholder so the chart still renders.

        Returns:
            Dict with 'labels' and 'datasets' for a Chart.js pie chart.
        """
        if PROPERTY_TYPE_COLUMN not in self.df.columns:
            # Graceful fallback — column is optional per SRS
            return {
                "labels": ["No PropertyType column in CSV"],
                "datasets": [{
                    "data":            [1],
                    "backgroundColor": ["#cccccc"],
                }],
            }

        counts = self.df[PROPERTY_TYPE_COLUMN].value_counts()

        # Cycle through PIE_COLORS if there are more types than defined colours
        colors = [PIE_COLORS[i % len(PIE_COLORS)] for i in range(len(counts))]

        return {
            "labels": list(counts.index),
            "datasets": [{
                "data":            [int(v) for v in counts.values],
                "backgroundColor": colors,
            }],
        }
