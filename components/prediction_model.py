# Implements SRS FR-4.1 (Model Training), FR-4.2 (Model Persistence),
#             FR-4.3 (Price Prediction)
"""
PredictionModel Component
--------------------------
Trains a Linear Regression model on property data, saves/loads it as Pickle
files, and predicts property prices with confidence information.
"""

import os
import pickle
from datetime import datetime

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error

# ── Folder + file constants ────────────────────────────────────────────────────
MODELS_FOLDER = "models"
MODEL_FILE    = "model.pkl"
ENCODER_FILE  = "encoder.pkl"
METADATA_FILE = "metadata.pkl"

# ── Feature columns ────────────────────────────────────────────────────────────
# BASE_FEATURES are always used.  OPTIONAL_FEATURES are added only when
# the CSV contains that column.
BASE_FEATURES     = ["Area", "Bedrooms", "Bathrooms"]
OPTIONAL_FEATURES = ["Age"]

# ── Train / test split ─────────────────────────────────────────────────────────
TEST_SIZE    = 0.20   # 20 % of data used for testing accuracy
RANDOM_STATE = 42     # fixed seed → same split every run (reproducible)

# ── Confidence thresholds (based on R² score) ─────────────────────────────────
HIGH_CONFIDENCE_R2   = 0.80   # R² ≥ 0.80 → "High"
MEDIUM_CONFIDENCE_R2 = 0.60   # R² ≥ 0.60 → "Medium", else "Low"

# ── Price range for lower / upper estimate ─────────────────────────────────────
PRICE_RANGE_PCT = 0.10   # ±10 % of predicted price

# ── Input validation bounds (same rules as FR-1.2) ────────────────────────────
MIN_AREA = 100;  MAX_AREA = 10000
MIN_BEDS = 1;    MAX_BEDS = 10
MIN_BATH = 1;    MAX_BATH = 8
MIN_AGE  = 0;    MAX_AGE  = 100


class PredictionModel:
    """Trains and uses a Linear Regression model for property price prediction."""

    def __init__(self):
        """Set up file paths and initialise empty model attributes."""
        # Create the models/ folder if it does not exist yet
        os.makedirs(MODELS_FOLDER, exist_ok=True)

        self.model_path    = os.path.join(MODELS_FOLDER, MODEL_FILE)
        self.encoder_path  = os.path.join(MODELS_FOLDER, ENCODER_FILE)
        self.metadata_path = os.path.join(MODELS_FOLDER, METADATA_FILE)

        # Filled by train() or load_model()
        self.model        = None
        self.encoder      = None
        self.metadata     = {}
        self.feature_cols = []   # e.g. ["Area","Bedrooms","Bathrooms"] or + "Age"

    # ── Training ───────────────────────────────────────────────────────────────

    def train(self, dataframe):
        """
        Train a Linear Regression model on the property dataset (FR-4.1).

        Steps:
          1. Decide which features to use (Age added only if column exists).
          2. LabelEncoder: convert Location text → integer (ML needs numbers).
          3. Build feature matrix X  (Location_Encoded + numeric features).
          4. train_test_split: 80 % training / 20 % testing.
          5. LinearRegression.fit() on the training set.
          6. Evaluate: R² score and MAE on the test set.
          7. Store model, encoder, metadata as instance attributes.

        Args:
            dataframe: Pandas DataFrame loaded from the uploaded CSV.

        Returns:
            Dict: {r2_score, mae, train_size, test_size, feature_cols}
        """
        # Step 1: Determine feature columns
        self.feature_cols = list(BASE_FEATURES)
        for col in OPTIONAL_FEATURES:
            if col in dataframe.columns:
                self.feature_cols.append(col)

        # Step 2: Encode Location (e.g. "Lahore"→0, "Karachi"→1, "Multan"→2)
        self.encoder = LabelEncoder()
        location_encoded = self.encoder.fit_transform(dataframe["Location"])

        # Step 3: Build feature matrix as a NumPy 2-D array
        # Column order: [Location_Encoded, Area, Bedrooms, Bathrooms, (Age)]
        feature_arrays = [location_encoded]
        for col in self.feature_cols:
            feature_arrays.append(dataframe[col].values)

        X = np.column_stack(feature_arrays)
        y = dataframe["Price"].values

        # Step 4: Split data — same random seed every time for reproducibility
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )

        # Step 5: Train the model
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)

        # Step 6: Evaluate on the held-out test set
        y_pred = self.model.predict(X_test)
        r2  = round(float(self.model.score(X_test, y_test)), 4)
        mae = round(float(mean_absolute_error(y_test, y_pred)), 2)

        # Step 7: Build metadata dict (saved to disk with save_model)
        self.metadata = {
            "r2_score":      r2,
            "mae":           mae,
            "training_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "feature_cols":  self.feature_cols,
            "train_size":    int(len(X_train)),
            "test_size":     int(len(X_test)),
            "total_records": int(len(dataframe)),
            "n_locations":   int(len(self.encoder.classes_)),
        }

        return {
            "r2_score":    r2,
            "mae":         mae,
            "train_size":  int(len(X_train)),
            "test_size":   int(len(X_test)),
            "feature_cols": self.feature_cols,
        }

    # ── Persistence ────────────────────────────────────────────────────────────

    def save_model(self):
        """
        Pickle the model, encoder, and metadata to the models/ folder (FR-4.2).

        Pickle = converts any Python object into a binary file on disk.
        On next app start we load these files instead of retraining.

        Returns:
            True if all three files saved successfully, False on any error.
        """
        try:
            with open(self.model_path,    "wb") as f:
                pickle.dump(self.model,    f)
            with open(self.encoder_path,  "wb") as f:
                pickle.dump(self.encoder,  f)
            with open(self.metadata_path, "wb") as f:
                pickle.dump(self.metadata, f)
            return True
        except Exception:
            return False

    def load_model(self):
        """
        Load the model, encoder, and metadata from pickle files (FR-4.2).

        Returns:
            True if all three files loaded successfully,
            False if any file is missing or unreadable.
        """
        if not self.is_trained():
            return False
        try:
            with open(self.model_path,    "rb") as f:
                self.model    = pickle.load(f)
            with open(self.encoder_path,  "rb") as f:
                self.encoder  = pickle.load(f)
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            # Restore feature list from metadata
            self.feature_cols = self.metadata.get("feature_cols", list(BASE_FEATURES))
            return True
        except Exception:
            return False

    def is_trained(self):
        """
        Check whether all three model files exist on disk.

        Returns:
            True if model is ready to use, False otherwise.
        """
        return (
            os.path.exists(self.model_path)   and
            os.path.exists(self.encoder_path) and
            os.path.exists(self.metadata_path)
        )

    # ── Validation ─────────────────────────────────────────────────────────────

    def validate_inputs(self, property_dict):
        """
        Validate property inputs before running a prediction (FR-4.3).

        Checks:
          - Location must be one the encoder saw during training.
          - Area: 100 – 10 000 sq ft.
          - Bedrooms: 1 – 10.
          - Bathrooms: 1 – 8.
          - Age: 0 – 100  (only if Age is in feature_cols).

        Args:
            property_dict: Dict with keys matching feature names.

        Returns:
            (True, [])  if all valid.
            (False, [list of error strings])  if any check fails.
        """
        errors = []
        known  = list(self.encoder.classes_) if self.encoder else []

        if property_dict.get("Location") not in known:
            errors.append(
                f"Location '{property_dict.get('Location')}' "
                "was not in the training dataset."
            )

        try:
            area = float(property_dict.get("Area", 0))
            if not (MIN_AREA <= area <= MAX_AREA):
                errors.append(f"Area must be between {MIN_AREA} and {MAX_AREA} sq ft.")
        except (ValueError, TypeError):
            errors.append("Area must be a valid number.")

        try:
            beds = int(property_dict.get("Bedrooms", 0))
            if not (MIN_BEDS <= beds <= MAX_BEDS):
                errors.append(f"Bedrooms must be between {MIN_BEDS} and {MAX_BEDS}.")
        except (ValueError, TypeError):
            errors.append("Bedrooms must be a valid number.")

        try:
            baths = int(property_dict.get("Bathrooms", 0))
            if not (MIN_BATH <= baths <= MAX_BATH):
                errors.append(f"Bathrooms must be between {MIN_BATH} and {MAX_BATH}.")
        except (ValueError, TypeError):
            errors.append("Bathrooms must be a valid number.")

        if "Age" in self.feature_cols:
            try:
                age = int(property_dict.get("Age", 0))
                if not (MIN_AGE <= age <= MAX_AGE):
                    errors.append(
                        f"Property age must be between {MIN_AGE} and {MAX_AGE} years."
                    )
            except (ValueError, TypeError):
                errors.append("Property age must be a valid number.")

        return (len(errors) == 0), errors

    # ── Prediction ─────────────────────────────────────────────────────────────

    def predict(self, property_dict):
        """
        Predict the price for a property using the trained model (FR-4.3).

        Assumes validate_inputs() was already called and passed successfully.

        Args:
            property_dict: Dict with Location, Area, Bedrooms, Bathrooms, (Age).

        Returns:
            Dict with predicted_price, price_lower, price_upper,
            confidence, r2_score, mae, training_date.
        """
        # Encode location to the integer seen during training
        location_encoded = float(
            self.encoder.transform([property_dict["Location"]])[0]
        )

        # Build feature row in exact same column order as during training
        row = [location_encoded]
        for feat in self.feature_cols:
            row.append(float(property_dict.get(feat, 0)))

        # Run the prediction
        predicted_price = float(self.model.predict([row])[0])

        # Price range: ±10 % of the predicted value
        price_lower = predicted_price * (1 - PRICE_RANGE_PCT)
        price_upper = predicted_price * (1 + PRICE_RANGE_PCT)

        # Confidence based on R²
        r2 = self.metadata.get("r2_score", 0)
        if r2 >= HIGH_CONFIDENCE_R2:
            confidence = "High"
        elif r2 >= MEDIUM_CONFIDENCE_R2:
            confidence = "Medium"
        else:
            confidence = "Low"

        return {
            "predicted_price": round(predicted_price, 2),
            "price_lower":     round(price_lower,     2),
            "price_upper":     round(price_upper,     2),
            "confidence":      confidence,
            "r2_score":        self.metadata.get("r2_score",     "N/A"),
            "mae":             self.metadata.get("mae",           "N/A"),
            "training_date":   self.metadata.get("training_date", "N/A"),
        }

    # ── Helpers ────────────────────────────────────────────────────────────────

    def get_locations(self):
        """
        Return a sorted list of location names the model was trained on.

        Used to populate the Location dropdown on the predict form.

        Returns:
            Sorted list of strings, or [] if the encoder is not loaded.
        """
        if self.encoder is None:
            return []
        return sorted(list(self.encoder.classes_))
