"""Alzheimer's Risk Screening — Stage 1 (teammate .keras + scaler).

Uses the teammate-supplied model and scaler (loaded ONCE at module import),
not per-request. Degrades gracefully when TensorFlow isn't installed by logging
and returning a placeholder message rather than crashing the endpoint.

Note: the model returns a probability (0-1); this service converts to a
0-100 score for UI consumption, plus a tier label and the feature-level
input received (no personal health disclosure in the JSON response).
"""
import os
import json
import logging
import pickle
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Feature list (34) — exact order from teammate's feature_names.json
FEATURE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml_models", "alzheimers_risk", "feature_names.json"
)
SCALER_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml_models", "alzheimers_risk", "scaler.pkl"
)
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml_models", "alzheimers_risk", "alzheimers_risk_model.keras"
)

FEATURE_NAMES: List[str] = []
_model = None
_scaler = None
_model_loaded = False


def _load_features() -> List[str]:
    try:
        with open(os.path.abspath(FEATURE_PATH), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _load_artifacts() -> bool:
    global _model, _scaler, _model_loaded, FEATURE_NAMES
    FEATURE_NAMES = _load_features()
    try:
        import tensorflow as tf
        # Keras 3.13.2 format (.keras) — load once at import
        _model = tf.keras.models.load_model(os.path.abspath(MODEL_PATH), compile=False)
        with open(os.path.abspath(SCALER_PATH), "rb") as f:
            import sklearn  # only import when needed
            try:
                import joblib
                _scaler = joblib.load(f)
            except Exception:
                f.seek(0)
                _scaler = pickle.load(f)
        _model_loaded = True
        logger.info("Risk-screening model loaded (%d features).", len(FEATURE_NAMES))
    except Exception as exc:
        logger.warning("Risk-screening artifacts unavailable (%s) — endpoint will return placeholder.", exc)
        _model = None
        _scaler = None
        _model_loaded = False
    return _model_loaded


# Load once at module import (lazy; doesn't block server start on missing tf)
try:
    _load_artifacts()
except Exception as exc:
    logger.info("Risk-screening deferred load: %s", exc)


# Simple validation rules mapped from model_input_guide.json
# Auto-derived dtype map from feature_names.json + model_input_guide.json.
# Anything that looks like a flag (int min=0 max=1) is treated as int; otherwise float.
# Kept as a fallback dict below for the features the guide doesn't explicitly tag.
FEATURE_DTYPE_MAP = {
    "Gender": int, "Ethnicity": int, "EducationLevel": int,
    "Smoking": int, "AlcoholConsumption": float,
    "PhysicalActivity": float, "DietQuality": float, "SleepQuality": float,
    "FamilyHistoryAlzheimers": int, "CardiovascularDisease": int,
    "Diabetes": int, "Depression": int, "HeadInjury": int,
    "Hypertension": int, "MMSE": float, "FunctionalAssessment": float,
    "MemoryComplaints": int, "BehavioralProblems": int,
    "ADL": float, "Confusion": int, "Disorientation": int,
    "PersonalityChanges": int, "DifficultyCompletingTasks": int,
    "Forgetfulness": int,
    "Age": int, "BMI": float, "SystolicBP": int, "DiastolicBP": int,
    "CholesterolTotal": float, "CholesterolLDL": float, "CholesterolHDL": float,
    "CholesterolTriglycerides": float,
}


def validate_input(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for feature in FEATURE_NAMES:
        if feature not in data:
            errors.append(f"missing_feature: {feature}")
        else:
            value = data[feature]
            if value is None:
                errors.append(f"null_feature: {feature}")
            else:
                try:
                    # Coerce to expected type; float/continuous accept int; int flags must be whole
                    expected = FEATURE_DTYPE_MAP.get(feature, float)
                    if expected == int:
                        float(value)  # must be numeric
                        if float(value) % 1 != 0:
                            errors.append(f"non_integer_feature: {feature}")
                    else:
                        float(value)
                except (TypeError, ValueError):
                    errors.append(f"bad_type: {feature} ({type(value).__name__})")
    return errors


def build_feature_array(data: Dict[str, Any]) -> Any:
    import numpy as np
    arr = np.array([[float(data.get(f, 0)) for f in FEATURE_NAMES]], dtype=np.float64)
    return arr


def run_inference(data: Dict[str, Any]) -> Dict[str, Any]:
    if not _model_loaded:
        return {
            "status": "model_unavailable",
            "message": "Risk-screening model not loaded (TensorFlow / .keras missing). "
                       "This endpoint requires a real backend environment with tensorflow installed.",
            "feature_count_received": len([k for k in data if k in FEATURE_NAMES]),
        }

    errors = validate_input(data)
    if errors:
        return {
            "status": "validation_failed",
            "errors": errors,
        }

    import numpy as np
    arr = build_feature_array(data)
    scaled = _scaler.transform(arr)  # sklearn StandardScaler
    prediction = float(_model.predict(scaled, verbose=0)[0][0])
    # Clamp to [0, 1] (model output contract per integration guide)
    prediction = max(0.0, min(1.0, prediction))
    # Convert probability to 0-100 scale for UI; keep tier label simple
    score = round(prediction * 100, 2)
    tier = (
        "low_risk" if score < 33 else
        ("moderate_risk" if score < 67 else "high_risk")
    )
    return {
        "status": "ok",
        "risk_score": score,  # 0-100 per teammate's spec (probability * 100)
        "probability": prediction,  # raw 0-1
        "tier": tier,
        "feature_count": len(FEATURE_NAMES),
        "note": "Preliminary screening only; not a clinical diagnosis",
    }
