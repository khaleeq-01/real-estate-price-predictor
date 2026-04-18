# Project: Web-Based Real Estate Price Prediction System

## Overview
Yeh Final Year Project (FYP Part 1) hai — Islamia University Bahawalpur.
Flask-based web application jo property data (CSV) upload karwa ke
statistical analysis, visualizations, aur Linear Regression se price
prediction provide karta hai.

Full requirements `docs/Software_Requirements_Specification...pdf` mein hain.
Full design `docs/sdd_real_estate.pdf` mein hai.
Har feature implement karte waqt in documents ko reference karo.

## Developer
- Name: Khaleeq Ur Rehman
- Level: Beginner (complete guide ki zaroorat hai)
- Goal: Data Analyst career, international market

## Tech Stack (Part 1 only)
- Backend: Python 3.8+, Flask 2.3+
- Data: Pandas 2.0+, NumPy 1.24+
- ML: Scikit-learn 1.3+ (Linear Regression only)
- Frontend: HTML5, CSS3, Vanilla JavaScript, Chart.js 4.0+ (via CDN)
- Storage: CSV files + Pickle (no database in Part 1)

## Folder Structure (SDD Appendix F)
project/
├── app.py
├── requirements.txt
├── CLAUDE.md
├── README.md
├── .gitignore
├── components/
│   ├── file_handler.py
│   ├── property_dataset.py
│   ├── data_analyzer.py
│   ├── visualizer.py
│   └── prediction_model.py
├── templates/
│   ├── home.html
│   ├── upload.html
│   ├── dashboard.html
│   └── predict.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── uploads/   (git-ignored)
├── models/    (git-ignored)
├── exports/   (git-ignored)
└── docs/      (SRS + SDD PDFs)

## Coding Rules
1. PEP 8 style guide follow karna (Python standard).
2. Har function/class ke upar docstring likhna — kya karta hai, inputs, outputs.
3. Comments simple English mein ho taakay beginner samajh sakay.
4. Functions 50 lines se chhoti rakhna.
5. Har file ke top par comment ho: "Implements SRS FR-X.X".
6. Hardcoded values (magic numbers) mat use karna — constants banao.

## Workflow Rules (IMPORTANT)
1. Koi bhi code likhne se PEHLE short plan batao, main approve karoonga.
2. Ek waqt mein ek milestone par kaam karo, aage mat bharo.
3. Bade changes se pehle mujhse pucho ("ye dekho, theek hai?").
4. Jab milestone complete ho, to:
   - Manual test instructions batao
   - Commit message suggest karo
   - Mujhse permission lo git commit + push ke liye
5. Mujhe beginner samjho — har technical term explain karo short mein.

## Git Workflow
- Har milestone ke end par: stage → commit → push.
- Commit messages clear ho: "Milestone 1: Flask skeleton + home route"
- Push karne se pehle meri confirmation lena.
- `.gitignore` mein: uploads/, models/, exports/, __pycache__/, .venv/, *.pkl, *.csv (except sample)

## Milestones
- [x] Milestone 1: Flask skeleton + folder structure + home page
- [x] Milestone 2: File upload + validation (FR-1)
- [x] Milestone 3: Analysis + visualization dashboard (FR-2, FR-3)
- [x] Milestone 4: ML model training + prediction (FR-4)
- [ ] Milestone 5: Export + polish + README (FR-5)

## References
- SRS: `docs/Software_Requirements_Specification_-_Real_Estate_Price_Prediction_System__Original__1_.pdf`
- SDD: `docs/sdd_real_estate__1_.pdf`