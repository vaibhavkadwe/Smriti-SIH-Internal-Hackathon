#!/usr/bin/env python3
"""End-to-end test: call run_inference() on each cohort's clinical_features."""
import os, sys
sys.path.insert(0, '/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend')

# Install joblib if not present
try:
    import joblib
except ImportError:
    os.system('uv pip install --python /Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/backend-verify/bin/python joblib')

from app.services.risk_screening_service import run_inference, _model_loaded

print(f"Model loaded: {_model_loaded}")
print()

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

import json
print("=" * 60)
print("Cohort A — Ranjana Devi (MMSE 21, multiple comorbidities)")
print("=" * 60)
r_a = run_inference(COHORT_A)
print(json.dumps(r_a, indent=2))

print()
print("=" * 60)
print("Cohort B — Aai Test (MMSE 27, healthy lifestyle)")
print("=" * 60)
r_b = run_inference(COHORT_B)
print(json.dumps(r_b, indent=2))

print()
print("=" * 60)
print("Summary")
print("=" * 60)
print(f"Cohort A status: {r_a.get('status')}, risk_score: {r_a.get('risk_score')}, tier: {r_a.get('tier')}")
print(f"Cohort B status: {r_b.get('status')}, risk_score: {r_b.get('risk_score')}, tier: {r_b.get('tier')}")
assert r_a.get("status") == "ok", f"Cohort A should be 'ok', got: {r_a}"
assert r_b.get("status") == "ok", f"Cohort B should be 'ok', got: {r_b}"
print("\n✓ Both cohorts returned real risk_score, not model_unavailable")
