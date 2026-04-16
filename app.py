# Implements SRS UI-1 (Home Page), UI-2 (Upload Page),
# UI-3 (Dashboard Page), UI-4 (Predict Page)

from flask import Flask, render_template

# Flask explanation: Flask is a lightweight Python web framework.
# It lets us define "routes" — URLs that the browser can visit.
# When a user visits a URL, Flask runs the matching function
# and returns an HTML page.

app = Flask(__name__)


@app.route("/")
def home():
    """Render the home page with the 4 navigation cards."""
    return render_template("home.html")


@app.route("/upload")
def upload():
    """Render the upload page (placeholder — full logic in Milestone 2)."""
    return render_template("upload.html")


@app.route("/dashboard")
def dashboard():
    """Render the dashboard page (placeholder — full logic in Milestone 3)."""
    return render_template("dashboard.html")


@app.route("/predict")
def predict():
    """Render the predict page (placeholder — full logic in Milestone 4)."""
    return render_template("predict.html")


# This block runs only when you execute app.py directly (not when imported).
# debug=True means Flask will auto-reload when you save a file — useful during development.
if __name__ == "__main__":
    app.run(debug=True)
