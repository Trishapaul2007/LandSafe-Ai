"""
ml_predict.py
--------------
Loads the trained landslide-risk model (exported from the Colab notebook) if present,
otherwise trains a fallback model on synthetic data automatically on startup so the
backend always works out of the box for a demo.

To use YOUR real trained model instead of the fallback:
1. In Colab, run the export cell (joblib.dump(...)) from BhuRakshak_Landslide_Risk_Prototype.ipynb
2. Download landslide_risk_model.pkl and landslide_scaler.pkl
3. Place both files in backend/models/
4. Restart the backend — it will load them automatically instead of training a fallback
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODELS_DIR, "landslide_risk_model.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "landslide_scaler.pkl")

FEATURES = [
    "rainfall_mm",
    "slope_angle",
    "soil_moisture_pct",
    "elevation_m",
    "distance_to_fault_km",
    "prev_landslide_count",
    "vegetation_cover_pct",
]


def _generate_synthetic_data(n_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rainfall_mm = rng.gamma(shape=2.0, scale=40, size=n_samples)
    slope_angle = rng.uniform(5, 60, n_samples)
    soil_moisture = rng.uniform(10, 100, n_samples)
    elevation = rng.uniform(50, 2200, n_samples)
    distance_to_fault_km = rng.exponential(scale=5, size=n_samples)
    prev_landslide_count = rng.poisson(lam=0.6, size=n_samples)
    vegetation_cover_pct = rng.uniform(0, 100, n_samples)

    risk_score = (
        0.028 * rainfall_mm
        + 0.045 * slope_angle
        + 0.02 * soil_moisture
        - 0.01 * vegetation_cover_pct
        - 0.15 * distance_to_fault_km
        + 0.6 * prev_landslide_count
        - 0.0008 * elevation
    )
    risk_prob = 1 / (1 + np.exp(-(risk_score - 3.5) / 2))
    landslide = rng.binomial(1, np.clip(risk_prob, 0, 1))

    return pd.DataFrame(
        {
            "rainfall_mm": rainfall_mm.round(1),
            "slope_angle": slope_angle.round(1),
            "soil_moisture_pct": soil_moisture.round(1),
            "elevation_m": elevation.round(0),
            "distance_to_fault_km": distance_to_fault_km.round(2),
            "prev_landslide_count": prev_landslide_count,
            "vegetation_cover_pct": vegetation_cover_pct.round(1),
            "landslide_occurred": landslide,
        }
    )


def _train_fallback_model():
    df = _generate_synthetic_data()
    X = df[FEATURES]
    y = df["landslide_occurred"]
    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train_scaled, y_train)

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    return model, scaler


def load_model():
    """Loads the real trained model if present in backend/models/, else trains a fallback."""
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("[ml_predict] Loaded trained model from backend/models/")
    else:
        print("[ml_predict] No trained model found — training a fallback model on synthetic data.")
        model, scaler = _train_fallback_model()
        print(f"[ml_predict] Fallback model trained and saved to {MODELS_DIR}")
    return model, scaler


# Load once at import time (used by the FastAPI app)
_model, _scaler = load_model()


def predict_risk(
    rainfall_mm: float,
    slope_angle: float,
    soil_moisture_pct: float,
    elevation_m: float,
    distance_to_fault_km: float,
    prev_landslide_count: int,
    vegetation_cover_pct: float,
):
    """Returns (risk_probability: float, risk_level: str) for one set of readings."""
    input_df = pd.DataFrame(
        [
            {
                "rainfall_mm": rainfall_mm,
                "slope_angle": slope_angle,
                "soil_moisture_pct": soil_moisture_pct,
                "elevation_m": elevation_m,
                "distance_to_fault_km": distance_to_fault_km,
                "prev_landslide_count": prev_landslide_count,
                "vegetation_cover_pct": vegetation_cover_pct,
            }
        ]
    )
    scaled = _scaler.transform(input_df[FEATURES])
    prob = float(_model.predict_proba(scaled)[0, 1])

    if prob < 0.25:
        level = "Low"
    elif prob < 0.5:
        level = "Moderate"
    elif prob < 0.75:
        level = "High"
    else:
        level = "Critical"

    return round(prob, 3), level
