#!/usr/bin/env python3
"""Standalone test: load model + scaler, run inference on demo cohorts."""
import json, pickle, sys, os

BASE = "/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/ml_models/alzheimers_risk"
sys.path.insert(0, "/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend")

FEATURE_NAMES = json.load(open(os.path.join(BASE, "feature_names.json")))
import joblib
scaler = joblib.load(os.path.join(BASE, "scaler.pkl"))

import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model(os.path.join(BASE, "alzheimers_risk_model.keras"), compile=False)
print(f"Model loaded: input shape {model.input_shape}, output shape {model.output_shape}")

COHORT_A = {
    "Age": 74.0, "Gender": 0, "Ethnicity": 0, "EducationLevel": 1, "BMI": 27.1,
    "Smoking": 1, "AlcoholConsumption": 2.3, "PhysicalActivity": 2.0, "DietQuality": 4.2,
    "SleepQuality": 5.1, "FamilyHistoryAlzheimers": 1, "CardiovascularDisease": 1,
    "Diabetes": 1, "Depression": 1, "HeadInjury": 0, "Hypertension": 1,
    "SystolicBP": 148, "DiastolicBP": 92, "CholesterolTotal": 234.0,
    "CholesterolLDL": 142.0, "CholesterolHDL": 42.0, "CholesterolTriglycerides": 185.0,
    "MMSE": 21.0, "FunctionalAssessment": 6.2, "MemoryComplaints": 1,
    "BehavioralProblems": 1, "ADL": 6.8, "Confusion": 0, "Disorientation": 1,
    "PersonalityChanges": 0, "DifficultyCompletingTasks": 1, "Forgetfulness": 1,
}
COHORT_B = {
    "Age": 67.0, "Gender": 0, "Ethnicity": 0, "EducationLevel": 2, "BMI": 23.4,
    "Smoking": 0, "AlcoholConsumption": 0.5, "PhysicalActivity": 7.5, "DietQuality": 8.8,
    "SleepQuality": 8.2, "FamilyHistoryAlzheimers": 0, "CardiovascularDisease": 0,
    "Diabetes": 0, "Depression": 0, "HeadInjury": 0, "Hypertension": 0,
    "SystolicBP": 122, "DiastolicBP": 78, "CholesterolTotal": 188.0,
    "CholesterolLDL": 105.0, "CholesterolHDL": 58.0, "CholesterolTriglycerides": 120.0,
    "MMSE": 27.0, "FunctionalAssessment": 9.1, "MemoryComplaints": 0,
    "BehavioralProblems": 0, "ADL": 9.4, "Confusion": 0, "Disorientation": 0,
    "PersonalityChanges": 0, "DifficultyCompletingTasks": 0, "Forgetfulness": 0,
}

def run(data, label):
    arr = np.array([[float(data[f]) for f in FEATURE_NAMES]], dtype=np.float64)
    scaled = scaler.transform(arr)
    prob = float(model.predict(scaled, verbose=0)[0][0])
    prob = max(0.0, min(1.0, prob))
    score = round(prob * 100, 2)
    tier = "low_risk" if score < 33 else ("moderate_risk" if score < 67 else "high_risk")
    print(f"\n{label}:")
    print(f"  probability = {prob:.4f}")
    print(f"  risk_score  = {score} / 100")
    print(f"  tier        = {tier}")
    return score, prob, tier

sa, pa, ta = run(COHORT_A, "Cohort A (moderate risk)")
sb, pb, tb = run(COHORT_B, "Cohort B (lower risk)")

print("\n--- Summary ---")
print(f"Cohort A: {sa}/100 ({ta})")
print(f"Cohort B: {sb}/100 ({tb})")
assert ta != "low_risk", "Cohort A should not be low risk"
assert tb == "low_risk", "Cohort B should be low risk"
print("\nAssertions passed: A > B, tiers correct.")
