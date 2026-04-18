# Implements SRS UI-1 (Home Page), UI-2 (Upload Page),
# UI-3 (Dashboard Page), UI-4 (Predict Page), FR-5.1 (Export)

import os
import csv
import io
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from components.file_handler import FileHandler
from components.property_dataset import PropertyDataset
from components.data_analyzer import DataAnalyzer
from components.visualizer import Visualizer
from components.prediction_model import PredictionModel

# Folder where exported CSV files are saved (git-ignored)
EXPORTS_FOLDER = "exports"

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

        # Step 6b: Auto-train the ML model (best-effort — upload still succeeds
        # even if training fails, so the try/except swallows any errors here).
        success_msg = f"File uploaded successfully! {record_count:,} records loaded."
        try:
            pred_model = PredictionModel()
            train_result = pred_model.train(dataset.dataframe)
            pred_model.save_model()
            success_msg += f" Model trained \u2014 R\u00b2\u2009=\u2009{train_result['r2_score']}."
        except Exception:
            pass  # Training failure is non-blocking

        flash(success_msg, "success")

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


@app.route("/predict", methods=["GET", "POST"])
def predict():
    """
    GET:  Load trained model, populate location dropdown, render empty form.
    POST: Read form inputs, validate, predict price, render results.

    Auto-train: if no model files exist but a CSV is in session, train first.
    If neither model nor CSV exists, redirect to /upload.
    """
    pred_model = PredictionModel()

    # ── Ensure model is loaded (train on-the-fly if needed) ──────────────────
    if not pred_model.load_model():
        filename = session.get("filename")
        if not filename:
            flash("Please upload a CSV file first to train the model.", "error")
            return redirect(url_for("upload"))

        # Auto-train from the file already in session
        handler  = FileHandler()
        dataset  = PropertyDataset()
        filepath = handler.get_file_path(filename)

        if not dataset.load_csv(filepath):
            flash("Could not reload your file. Please upload again.", "error")
            return redirect(url_for("upload"))

        try:
            pred_model.train(dataset.dataframe)
            pred_model.save_model()
        except Exception:
            flash("Model training failed. Please upload your CSV again.", "error")
            return redirect(url_for("upload"))

    locations = pred_model.get_locations()
    metadata  = pred_model.metadata
    has_age   = "Age" in pred_model.feature_cols

    # ── GET: render empty form ────────────────────────────────────────────────
    if request.method == "GET":
        return render_template(
            "predict.html",
            locations=locations,
            metadata=metadata,
            has_age=has_age,
            result=None,
            form_data={},
        )

    # ── POST: validate inputs and run prediction ──────────────────────────────
    # Keep raw strings so we can re-populate the form on validation failure
    form_data = {
        "Location":  request.form.get("Location",  ""),
        "Area":      request.form.get("Area",      ""),
        "Bedrooms":  request.form.get("Bedrooms",  ""),
        "Bathrooms": request.form.get("Bathrooms", ""),
        "Age":       request.form.get("Age",       "0"),
    }

    # Convert to correct Python types for the model
    try:
        property_dict = {
            "Location":  form_data["Location"],
            "Area":      float(form_data["Area"]),
            "Bedrooms":  int(form_data["Bedrooms"]),
            "Bathrooms": int(form_data["Bathrooms"]),
            "Age":       int(form_data["Age"] or 0),
        }
    except (ValueError, TypeError):
        flash("Please enter valid numbers for Area, Bedrooms, and Bathrooms.", "error")
        return render_template(
            "predict.html",
            locations=locations,
            metadata=metadata,
            has_age=has_age,
            result=None,
            form_data=form_data,
        )

    # Validate ranges and location
    is_valid, errors = pred_model.validate_inputs(property_dict)
    if not is_valid:
        for error in errors:
            flash(error, "error")
        return render_template(
            "predict.html",
            locations=locations,
            metadata=metadata,
            has_age=has_age,
            result=None,
            form_data=form_data,
        )

    # Run prediction and render results
    result = pred_model.predict(property_dict)
    return render_template(
        "predict.html",
        locations=locations,
        metadata=metadata,
        has_age=has_age,
        result=result,
        form_data=form_data,
    )


@app.route("/export")
def export():
    """
    Generate a 3-section analysis CSV and send it as a download (SRS FR-5.1).

    send_file() explanation: Flask sends the saved file to the user's browser
    as a download (Content-Disposition: attachment). The browser shows a
    "Save file" dialog without reloading the current page.

    CSV sections:
      1. Summary Statistics  — price stats (mean, median, std, Q1, Q3, min, max)
      2. Location Analysis   — per-location average, min, max, count
      3. Raw Data            — every original row from the uploaded CSV
    """
    # Step 1: Ensure a file has been uploaded
    filename = session.get("filename")
    if not filename:
        flash("Please upload a CSV file first.", "error")
        return redirect(url_for("upload"))

    # Step 2: Load the dataset
    handler = FileHandler()
    dataset = PropertyDataset()
    filepath = handler.get_file_path(filename)

    if not dataset.load_csv(filepath):
        flash("Could not load the dataset. Please upload again.", "error")
        return redirect(url_for("upload"))

    # Step 3: Run analysis for the summary sections
    analyzer      = DataAnalyzer(dataset.dataframe)
    stats         = analyzer.calculate_statistics()
    location_data = analyzer.location_analysis()

    # Step 4: Build the entire CSV content in memory (StringIO = in-RAM text file)
    output = io.StringIO()
    writer = csv.writer(output)

    # ── Section 1: Summary Statistics ────────────────────────────────────────
    writer.writerow(["SECTION: Summary Statistics"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total Properties",        stats["count"]])
    writer.writerow(["Mean Price (PKR)",         stats["mean"]])
    writer.writerow(["Median Price (PKR)",       stats["median"]])
    writer.writerow(["Std Deviation (PKR)",      stats["std"]])
    writer.writerow(["Min Price (PKR)",          stats["min"]])
    writer.writerow(["Max Price (PKR)",          stats["max"]])
    writer.writerow(["Q1 - 25th Pctile (PKR)",  stats["q1"]])
    writer.writerow(["Q3 - 75th Pctile (PKR)",  stats["q3"]])
    writer.writerow([])  # blank line separates sections

    # ── Section 2: Location Analysis ─────────────────────────────────────────
    writer.writerow(["SECTION: Location Analysis"])
    writer.writerow(["Location", "Avg Price (PKR)", "Min Price (PKR)",
                     "Max Price (PKR)", "Property Count"])
    for loc in location_data:
        writer.writerow([
            loc["location"],
            loc["avg_price"],
            loc["min_price"],
            loc["max_price"],
            loc["count"],
        ])
    writer.writerow([])  # blank line separates sections

    # ── Section 3: Raw Data ───────────────────────────────────────────────────
    writer.writerow(["SECTION: Raw Data"])
    # to_csv() returns the full DataFrame as a CSV string — write it directly
    output.write(dataset.dataframe.to_csv(index=False))

    # Step 5: Save the built CSV to the exports/ folder
    os.makedirs(EXPORTS_FOLDER, exist_ok=True)
    export_filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    export_path     = os.path.join(EXPORTS_FOLDER, export_filename)

    with open(export_path, "w", encoding="utf-8") as f:
        f.write(output.getvalue())

    # Step 6: Flash message — stored in session, shown on next page navigation
    flash(f"Export complete \u2014 {export_filename} downloaded.", "success")

    # Step 7: Send the file to the browser as a download
    return send_file(
        os.path.abspath(export_path),
        mimetype="text/csv",
        as_attachment=True,
        download_name=export_filename,
    )


# This block runs only when you execute app.py directly (not when imported).
# debug=True means Flask auto-reloads when you save a file — useful during development.
if __name__ == "__main__":
    app.run(debug=True)
