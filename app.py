# Implements SRS UI-1 (Home Page), UI-2 (Upload Page),
# UI-3 (Dashboard Page), UI-4 (Predict Page)

from flask import Flask, render_template, request, redirect, url_for, flash, session
from components.file_handler import FileHandler
from components.property_dataset import PropertyDataset
from components.data_analyzer import DataAnalyzer
from components.visualizer import Visualizer

app = Flask(__name__)

# secret_key is required for Flask sessions and flash messages to work.
# A session is like a small notepad Flask keeps for each user (in an encrypted
# browser cookie) — we use it to remember which file was uploaded.
# Flash messages are one-time notifications shown after a redirect.
# NOTE: In production, use a random secret from an environment variable.
#       A hardcoded key is acceptable for FYP development only.
app.secret_key = "fyp-real-estate-dev-key-2025"


# ── Custom template filters ────────────────────────────────────────────────────
# Template filters let us format values inside HTML templates using the | symbol.
# Example in template: {{ 15000000 | format_price }} → "15,000,000 PKR"

@app.template_filter("format_price")
def format_price(value):
    """Format a numeric price as '15,000,000 PKR' with thousands separators."""
    try:
        return f"{int(value):,} PKR"
    except (ValueError, TypeError):
        return value


@app.template_filter("format_number")
def format_number(value):
    """Format a number with thousands separators (e.g. 2,500)."""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Render the home page with the 4 navigation cards."""
    return render_template("home.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """
    GET:  Show the upload form.
    POST: Validate and save the uploaded CSV, then render a data preview.

    Flow on POST:
    1. Validate file (extension + size)   → flash error and redirect on failure
    2. Save file to uploads/              → flash error on failure
    3. Load CSV into DataFrame            → flash error on failure, delete file
    4. Validate data structure/values     → flash all errors, delete file
    5. Store filename in session          → so Dashboard/Predict can load it
    6. Render upload.html with preview
    """
    preview = None
    record_count = 0

    if request.method == "POST":
        file = request.files.get("file")
        handler = FileHandler()

        # Step 1: Validate file format and size
        is_valid, error_msg = handler.validate_file(file)
        if not is_valid:
            flash(error_msg, "error")
            return redirect(url_for("upload"))

        # Step 2: Save to uploads/ folder
        filename = handler.save_file(file)
        if filename is None:
            flash("Failed to save the file. Please try again.", "error")
            return redirect(url_for("upload"))

        # Step 3: Load CSV into a DataFrame
        dataset = PropertyDataset()
        filepath = handler.get_file_path(filename)
        if not dataset.load_csv(filepath):
            handler.delete_file(filename)
            flash("Could not read the CSV file. Make sure it is a valid CSV.", "error")
            return redirect(url_for("upload"))

        # Step 4: Validate columns and value ranges
        is_valid, errors = dataset.validate_data()
        if not is_valid:
            handler.delete_file(filename)
            for error in errors:
                flash(error, "error")
            return redirect(url_for("upload"))

        # Step 5: Remember this file for the rest of the session
        session["filename"] = filename

        # Step 6: Prepare preview data for the template
        preview = dataset.get_preview(20)
        record_count = dataset.record_count
        flash(f"File uploaded successfully! {record_count:,} records loaded.", "success")

    return render_template("upload.html", preview=preview, record_count=record_count)


@app.route("/dashboard")
def dashboard():
    """
    Load the uploaded dataset, run analysis, generate chart data,
    and render the full dashboard page (SRS FR-2, FR-3).

    Flow:
    1. Check session for an uploaded filename — redirect to /upload if missing.
    2. Load the CSV into a DataFrame via PropertyDataset.
    3. Run DataAnalyzer: statistics, location analysis, correlations.
    4. Run Visualizer: bar chart, scatter plot, pie chart data.
    5. Pass everything to dashboard.html.
    """
    # Step 1: Ensure a file was uploaded in this session
    filename = session.get("filename")
    if not filename:
        flash("Please upload a CSV file first.", "error")
        return redirect(url_for("upload"))

    # Step 2: Load the saved CSV file
    handler = FileHandler()
    dataset = PropertyDataset()
    filepath = handler.get_file_path(filename)

    if not dataset.load_csv(filepath):
        flash("Could not load your file. Please upload it again.", "error")
        session.pop("filename", None)
        return redirect(url_for("upload"))

    # Step 3: Statistical analysis
    analyzer     = DataAnalyzer(dataset.dataframe)
    stats        = analyzer.calculate_statistics()
    location_data = analyzer.location_analysis()
    correlations = analyzer.correlation_analysis()

    # Step 4: Chart data (Python dicts — Jinja2 tojson filter converts to JS)
    visualizer    = Visualizer(dataset.dataframe)
    bar_chart     = visualizer.generate_bar_chart()
    scatter_chart = visualizer.generate_scatter_plot()
    pie_chart     = visualizer.generate_pie_chart()

    return render_template(
        "dashboard.html",
        stats=stats,
        location_data=location_data,
        correlations=correlations,
        bar_chart=bar_chart,
        scatter_chart=scatter_chart,
        pie_chart=pie_chart,
    )


@app.route("/predict")
def predict():
    """Render the predict page (placeholder — full logic in Milestone 4)."""
    return render_template("predict.html")


# This block runs only when you execute app.py directly (not when imported).
# debug=True means Flask auto-reloads when you save a file — useful during development.
if __name__ == "__main__":
    app.run(debug=True)
