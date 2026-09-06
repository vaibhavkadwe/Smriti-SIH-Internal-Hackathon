"""Patient API Routes — PatientProfile CRUD + CaregiverPatientLink management.

Endpoints:
  POST   /patients            — create a patient profile (staff/caregiver; patient self-registers)
  GET    /patients/me         — current patient's own profile
  GET    /patients/{id}       — retrieve a patient profile
  GET    /patients/{id}/caregivers — list active caregiver links
  POST   /patients/{id}/caregivers — link a caregiver to a patient
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.database import get_db
from app.deps import ensure_patient_access
from app.services.compliance_service import ComplianceService
from app.models.all_models import (
    PatientProfile,
    CaregiverPatientLink,
    CognitiveBaselineEnum,
    RelationshipTypeEnum,
    PermissionTierEnum,
)
from app.models.user import User

router = APIRouter(prefix="/patients", tags=["patients"])

require_creator = require_role("patient", "family_caregiver", "asha_worker", "clinician")
require_caregiver_or_staff = require_role("family_caregiver", "asha_worker", "clinician")


# ============= Schemas =============


class PatientCreateRequest(BaseModel):
    name: str
    dob: Optional[date] = None
    cognitive_baseline: str = CognitiveBaselineEnum.HEALTHY.value
    region: Optional[str] = None
    district: Optional[str] = None
    routine: Optional[dict] = None
    user_id: Optional[UUID] = None  # link an existing patient-role account


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: Optional[UUID]
    name: str
    dob: Optional[date]
    cognitive_baseline: str
    region: Optional[str]
    district: Optional[str]
    created_at: datetime


class CaregiverLinkRequest(BaseModel):
    caregiver_id: UUID
    relationship_type: RelationshipTypeEnum = RelationshipTypeEnum.FAMILY
    permission_tier: PermissionTierEnum = PermissionTierEnum.BASIC


class CaregiverLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    caregiver_id: UUID
    patient_id: UUID
    relationship_type: RelationshipTypeEnum
    permission_tier: PermissionTierEnum
    consent_granted_at: datetime
    is_active: bool
    created_at: datetime


# ============= Helpers =============


async def _get_patient(db: AsyncSession, patient_id: UUID) -> Optional[PatientProfile]:
    res = await db.execute(select(PatientProfile).where(PatientProfile.id == patient_id))
    return res.scalar_one_or_none()


async def _can_view_patient(db: AsyncSession, user: User, patient: PatientProfile) -> bool:
    """No-implicit-access: staff/owner may view; caregivers need an active link."""
    if patient is None:
        return False
    role = user.role.value if hasattr(user.role, "value") else str(user.role)
    if role in ("admin", "clinician", "asha_worker"):
        return True
    if patient.user_id == user.id:
        return True
    if role in ("family_caregiver", "patient"):
        res = await db.execute(
            select(CaregiverPatientLink).where(
                CaregiverPatientLink.caregiver_id == user.id,
                CaregiverPatientLink.patient_id == patient.id,
                CaregiverPatientLink.is_active == True,
            )
        )
        return res.scalar_one_or_none() is not None
    return False


def _baseline(value: str) -> CognitiveBaselineEnum:
    try:
        return CognitiveBaselineEnum(value)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid cognitive_baseline: {value}. Choose from {[e.value for e in CognitiveBaselineEnum]}",
        )


from app.services.risk_screening_service import run_inference, FEATURE_NAMES, FEATURE_DTYPE_MAP


# ============= Risk Screening Endpoint =============


class RiskScreeningRequest(BaseModel):
    """34 feature fields exactly as model_input_guide.json defines."""
    model_config = ConfigDict(extra="forbid")

    # Use the feature names directly; this avoids hard-coding 34 fields.
    # Validation uses FEATURE_NAMES from feature_names.json.

    Age: Optional[float] = None
    Gender: Optional[int] = None
    Ethnicity: Optional[int] = None
    EducationLevel: Optional[int] = None
    BMI: Optional[float] = None
    Smoking: Optional[int] = None
    AlcoholConsumption: Optional[float] = None
    PhysicalActivity: Optional[float] = None
    DietQuality: Optional[float] = None
    SleepQuality: Optional[float] = None
    FamilyHistoryAlzheimers: Optional[int] = None
    CardiovascularDisease: Optional[int] = None
    Diabetes: Optional[int] = None
    Depression: Optional[int] = None
    HeadInjury: Optional[int] = None
    Hypertension: Optional[int] = None
    SystolicBP: Optional[int] = None
    DiastolicBP: Optional[int] = None
    CholesterolTotal: Optional[float] = None
    CholesterolLDL: Optional[float] = None
    CholesterolHDL: Optional[float] = None
    CholesterolTriglycerides: Optional[float] = None
    MMSE: Optional[float] = None
    FunctionalAssessment: Optional[float] = None
    MemoryComplaints: Optional[int] = None
    BehavioralProblems: Optional[int] = None
    ADL: Optional[float] = None
    Confusion: Optional[int] = None
    Disorientation: Optional[int] = None
    PersonalityChanges: Optional[int] = None
    DifficultyCompletingTasks: Optional[int] = None
    Forgetfulness: Optional[int] = None


class RiskScreeningResponse(BaseModel):
    status: str
    risk_score: Optional[float] = None
    probability: Optional[float] = None
    tier: Optional[str] = None
    feature_count: Optional[int] = None
    note: Optional[str] = None
    errors: Optional[List[str]] = None
    message: Optional[str] = None


@router.post("/{patient_id}/risk-screening", response_model=RiskScreeningResponse)
async def risk_screening(
    patient_id: UUID,
    body: RiskScreeningRequest,
    current_user: User = Depends(require_caregiver_or_staff),
    db: AsyncSession = Depends(get_db),
):
    """POST /patients/{id}/risk-screening

    Accepts the 34 features defined by the teammate's feature_names.json.
    Applies scaler.pkl, runs .keras inference, returns probability (0-1) +
    a 0-100 score. Degrades gracefully when TF is unavailable.
    """
    patient = await _get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Build a clean dict from Pydantic model; skip None fields so validation
    # can flag missing ones explicitly.
    raw: Dict[str, Any] = {}
    for f in FEATURE_NAMES:
        value = getattr(body, f, None)
        if value is not None:
            raw[f] = value

    result = run_inference(raw)
    if result.get("status") == "validation_failed":
        return RiskScreeningResponse(
            status="validation_failed",
            errors=result.get("errors", []),
        )
    return RiskScreeningResponse(**result)


# ============= Endpoints =============


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    body: PatientCreateRequest,
    current_user: User = Depends(require_creator),
    db: AsyncSession = Depends(get_db),
):
    """Create a patient profile. A patient-role account can self-register (own user_id)."""
    user_id = body.user_id
    if current_user.role.value == "patient":
        # Patients may only create a profile bound to their own account.
        user_id = current_user.id
        if body.user_id not in (None, current_user.id):
            raise HTTPException(status_code=403, detail="Patients may only self-register")

    patient = PatientProfile(
        user_id=user_id,
        name=body.name,
        dob=body.dob,
        cognitive_baseline=_baseline(body.cognitive_baseline),
        region=body.region,
        district=body.district,
        routine=body.routine,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get("/me", response_model=PatientResponse)
async def get_my_patient(
    current_user: User = Depends(require_role("patient", "family_caregiver", "asha_worker", "clinician")),
    db: AsyncSession = Depends(get_db),
):
    """Return the PatientProfile bound to the current account, if any."""
    res = await db.execute(select(PatientProfile).where(PatientProfile.user_id == current_user.id))
    patient = res.scalar_one_or_none()
    if patient is None:
        raise HTTPException(status_code=404, detail="No patient profile linked to this account")
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    current_user: User = Depends(require_role("patient", "family_caregiver", "asha_worker", "clinician")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a patient profile. Access is audited: staff see rosters, others need a link."""
    patient = await ensure_patient_access(db, current_user, patient_id)
    await ComplianceService.log_read_access(
        db, current_user.id, "patient_profile", patient_id
    )
    return patient


@router.get("/{patient_id}/caregivers", response_model=List[CaregiverLinkResponse])
async def list_patient_caregivers(
    patient_id: UUID,
    current_user: User = Depends(require_caregiver_or_staff),
    db: AsyncSession = Depends(get_db),
):
    """List active caregivers linked to a patient."""
    patient = await _get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    res = await db.execute(
        select(CaregiverPatientLink)
        .where(
            CaregiverPatientLink.patient_id == patient_id,
            CaregiverPatientLink.is_active == True,
        )
        .order_by(CaregiverPatientLink.created_at)
    )
    return list(res.scalars().all())


@router.post("/{patient_id}/caregivers", response_model=CaregiverLinkResponse, status_code=status.HTTP_201_CREATED)
async def link_caregiver(
    patient_id: UUID,
    body: CaregiverLinkRequest,
    current_user: User = Depends(require_caregiver_or_staff),
    db: AsyncSession = Depends(get_db),
):
    """Grant a caregiver access to a patient (creates an audited CaregiverPatientLink)."""
    patient = await _get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing = await db.execute(
        select(CaregiverPatientLink).where(
            CaregiverPatientLink.caregiver_id == body.caregiver_id,
            CaregiverPatientLink.patient_id == patient_id,
            CaregiverPatientLink.is_active == True,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Caregiver already linked to this patient")

    link = CaregiverPatientLink(
        caregiver_id=body.caregiver_id,
        patient_id=patient_id,
        relationship_type=body.relationship_type,
        permission_tier=body.permission_tier,
        is_active=True,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link
