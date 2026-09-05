"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.user import RoleEnum


# --- Auth ---

class RegisterRequest(BaseModel):
    phone: str
    email: Optional[str] = None
    password: str
    role: RoleEnum = RoleEnum.PATIENT
    preferred_language: str = "english"

class LoginRequest(BaseModel):
    phone: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: UUID
    phone: str
    email: Optional[str]
    role: RoleEnum
    preferred_language: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Patient ---

class PatientCreate(BaseModel):
    name: str
    dob: Optional[str] = None  # ISO date string
    cognitive_baseline: str = "healthy"
    region: Optional[str] = None
    district: Optional[str] = None
    routine: Optional[dict] = None

class PatientOut(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    name: str
    cognitive_baseline: str
    region: Optional[str]
    district: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Game Session ---

class GameSessionOut(BaseModel):
    id: UUID
    patient_id: UUID
    game_type: str
    difficulty_level: int
    attempts: int
    correct_count: int
    incorrect_count: int
    avg_response_time_ms: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Health ---

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
