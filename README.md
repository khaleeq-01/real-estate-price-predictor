# Real Estate Price Prediction System

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3+-000000?style=flat&logo=flask&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=flat&logo=scikit-learn&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.0+-FF6384?style=flat)

A web-based application that allows users to upload a property dataset (CSV), explore
statistical insights through interactive charts, and predict property prices using a
Linear Regression model — built as Final Year Project (Part 2) at Islamia University Bahawalpur.

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Upload** | Upload a CSV dataset with validation (columns, size, value ranges) |
| 2 | **Statistical Analysis** | Descriptive stats, location-wise analysis, price correlations |
| 3 | **Visualization** | Bar chart, scatter plot, pie chart powered by Chart.js |
| 4 | **Price Prediction** | Linear Regression model with R² score, MAE, and confidence level |
| 5 | **Export** | Download a 3-section analysis report (stats + location + raw data) as CSV |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.8+, Flask 2.3+ |
| Data Processing | Pandas 2.0+, NumPy 1.24+ |
| Machine Learning | scikit-learn 1.3+ (Linear Regression) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Chart.js 4.0+ (via CDN) |
| Model Storage | Pickle (`.pkl` files) |
| Dataset Storage | CSV files |

---

## How to Run

**Step 1 — Clone the repository**
```bash
git clone https://github.com/khaleeq-01/real-estate-price-predictor.git
cd real-estate-price-predictor
```

**Step 2 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — Start the Flask development server**
```bash
python app.py
```

**Step 4 — Open in browser**
```
http://127.0.0.1:5000
```

> **Note:** Upload a CSV file first. Required columns: `Location, Price, Area, Bedrooms, Bathrooms`.
> Minimum 100 records. The ML model is trained automatically after every upload.

---

## Project Structure

```
real-estate-predictor/
├── app.py                    # Flask routes: home, upload, dashboard, predict, export
├── requirements.txt          # Python dependencies
├── CLAUDE.md                 # Project instructions for Claude Code AI
├── README.md                 # This file
├── .gitignore
│
├── components/               # Business logic (one class per file)
│   ├── file_handler.py       # FR-1.1: file upload, save, delete
│   ├── property_dataset.py   # FR-1.2: CSV loading and validation
│   ├── data_analyzer.py      # FR-2:   statistical + location + correlation analysis
│   ├── visualizer.py         # FR-3:   Chart.js-compatible JSON generation
│   └── prediction_model.py   # FR-4:   Linear Regression train / save / predict
│
├── templates/                # Jinja2 HTML templates
│   ├── home.html
│   ├── upload.html
│   ├── dashboard.html
│   └── predict.html
│
├── static/
│   └── css/style.css         # All page styles
│
├── uploads/                  # Uploaded CSVs (git-ignored)
├── models/                   # Trained model pickle files (git-ignored)
├── exports/                  # Exported analysis CSVs (git-ignored)
└── docs/                     # SRS and SDD reference documents
```

---

## Screenshots

> Screenshots will be added after final testing.

| Page | Preview |
|------|---------|
| Home | `Docs/Screenshots/home.png` |
| Upload + Preview | `Docs/Screenshots/upload.png` |
| Dashboard (Charts) | `Docs/Screenshots/dashboard.png` |
| Predict (Results) | `Docs/Screenshots/predict.png` |

---

## Model Performance

The system uses **Linear Regression** (scikit-learn) trained on the uploaded dataset
with an 80/20 train/test split.

| Metric | Typical Range | What It Means |
|--------|--------------|---------------|
| **R² Score** | 0.75 – 0.90 | Model explains 75–90% of price variation. 1.0 = perfect. |
| **MAE** | 300,000 – 800,000 PKR | Average prediction is off by this amount. Lower = better. |

> Actual values depend on your dataset. The app displays the real R² and MAE
> after training on your uploaded CSV.

**Features used by the model:**
- `Location` (Label Encoded — text converted to integer)
- `Area` (sq ft)
- `Bedrooms`
- `Bathrooms`
- `Age` (years, if present in your CSV)

---

## Future Improvements (Part 2)

- **Database integration** — PostgreSQL or SQLite to persist datasets across sessions
- **Advanced ML models** — Random Forest, XGBoost, ensemble methods for better accuracy
- **User authentication** — login/signup so each user manages their own data
- **Cloud deployment** — host on Railway, Heroku, or AWS for public access
- **Real-time data** — integration with property portals (Zameen.com API)
- **Interactive maps** — Leaflet.js map showing price heatmap by location
- **REST API** — expose prediction endpoint for external applications

---

## Author

**Khaleeq Ur Rehman**

- University: Islamia University Bahawalpur (IUB)
- Program: BS Computer Science — Final Year
- Email: khaleeq.dataanalyst@gmail.com
- GitHub: [@khaleeq-01](https://github.com/khaleeq-01)
- LinkedIn: *[Add your LinkedIn URL here]*

---

*Built with Python + Flask as FYP Part 2 (Final) — Islamia University Bahawalpur, 2025*
