"""DEMO ONLY — seed realistic clinical values for the risk-screening pitch.

This is NOT a real intake form. The 32 feature values below are placeholder
estimates used solely to demonstrate the risk-screening card on the caregiver
dashboard. A production clinical intake (restricted to ASHA-worker / clinician
tier, with proper validation and consent) is still required before this system
can be used with actual patients.

Usage:
    cd backend
    DATABASE_URL=postgresql+psycopg://... alembic upgrade head   # apply 0005 first
    DATABASE_URL=... .venv/bin/python demo_clinical_seed.py
"""
import asyncio

from sqlalchemy import select

from app.database import async_session_maker
from app.models.all_models import PatientProfile

# The 32 features in exact order from ml_models/alzheimers_risk/feature_names.json
FEATURE_NAMES = [
    "Age", "Gender", "Ethnicity", "EducationLevel", "BMI",
    "Smoking", "AlcoholConsumption", "PhysicalActivity", "DietQuality", "SleepQuality",
    "FamilyHistoryAlzheimers", "CardiovascularDisease", "Diabetes", "Depression",
    "HeadInjury", "Hypertension", "SystolicBP", "DiastolicBP",
    "CholesterolTotal", "CholesterolLDL", "CholesterolHDL", "CholesterolTriglycerides",
    "MMSE", "FunctionalAssessment", "MemoryComplaints", "BehavioralProblems",
    "ADL", "Confusion", "Disorientation", "PersonalityChanges",
    "DifficultyCompletingTasks", "Forgetfulness",
]

# --- Cohort A: Moderate-risk patient (MMSE 21/30, multiple comorbidities) -----
COHORT_A = {
    "Age": 74.0,
    "Gender": 0,  # encoded value
    "Ethnicity": 0,
    "EducationLevel": 1,  # primary only
    "BMI": 27.1,
    "Smoking": 1,
    "AlcoholConsumption": 2.3,
    "PhysicalActivity": 2.0,
    "DietQuality": 4.2,
    "SleepQuality": 5.1,
    "FamilyHistoryAlzheimers": 1,  # yes
    "CardiovascularDisease": 1,
    "Diabetes": 1,
    "Depression": 1,
    "HeadInjury": 0,
    "Hypertension": 1,
    "SystolicBP": 148,
    "DiastolicBP": 92,
    "CholesterolTotal": 234.0,
    "CholesterolLDL": 142.0,
    "CholesterolHDL": 42.0,
    "CholesterolTriglycerides": 185.0,
    "MMSE": 21.0,  # mild cognitive impairment range
    "FunctionalAssessment": 6.2,
    "MemoryComplaints": 1,
    "BehavioralProblems": 1,
    "ADL": 6.8,
    "Confusion": 0,
    "Disorientation": 1,
    "PersonalityChanges": 0,
    "DifficultyCompletingTasks": 1,
    "Forgetfulness": 1,
}

# --- Cohort B: Lower-risk patient (MMSE 27/30, healthy lifestyle) ---------
COHORT_B = {
    "Age": 67.0,
    "Gender": 0,
    "Ethnicity": 0,
    "EducationLevel": 2,  # secondary
    "BMI": 23.4,
    "Smoking": 0,
    "AlcoholConsumption": 0.5,
    "PhysicalActivity": 7.5,
    "DietQuality": 8.8,
    "SleepQuality": 8.2,
    "FamilyHistoryAlzheimers": 0,
    "CardiovascularDisease": 0,
    "Diabetes": 0,
    "Depression": 0,
    "HeadInjury": 0,
    "Hypertension": 0,
    "SystolicBP": 122,
    "DiastolicBP": 78,
    "CholesterolTotal": 188.0,
    "CholesterolLDL": 105.0,
    "CholesterolHDL": 58.0,
    "CholesterolTriglycerides": 120.0,
    "MMSE": 27.0,  # normal range
    "FunctionalAssessment": 9.1,
    "MemoryComplaints": 0,
    "BehavioralProblems": 0,
    "ADL": 9.4,
    "Confusion": 0,
    "Disorientation": 0,
    "PersonalityChanges": 0,
    "DifficultyCompletingTasks": 0,
    "Forgetfulness": 0,
}


async def main() -> None:
    async with async_session_maker() as db:
        # Assign cohort A to the seeded demo patient (Ranjana Devi).
        res = await db.execute(select(PatientProfile).order_by(PatientProfile.created_at))
        patients = res.scalars().all()

        if not patients:
            print("No PatientProfile rows found. Run seed_demo.py first.")
            return

        assigned = 0
        for i, patient in enumerate(patients):
            cohort = COHORT_A if i == 0 else COHORT_B
            patient.clinical_features = {f: cohort[f] for f in FEATURE_NAMES}
            db.add(patient)
            assigned += 1

        await db.commit()
        print(f"Assigned clinical features to {assigned} patient(s):")
        for i, patient in enumerate(patients):
            cohort_name = "Cohort A (moderate risk)" if i == 0 else "Cohort B (lower risk)"
            mmse = patients[i].clinical_features.get("MMSE")
            print(f"  {patient.name} [{patient.id}] — {cohort_name}, MMSE={mmse}")


if __name__ == "__main__":
    asyncio.run(main())
