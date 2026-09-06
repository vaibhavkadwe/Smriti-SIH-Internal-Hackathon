from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from app.models.base import Base, enum_values

class RoleEnum(str, Enum):
    PATIENT = "patient"
    FAMILY_CAREGIVER = "family_caregiver"
    ASHA_WORKER = "asha_worker"
    CLINICIAN = "clinician"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum, values_callable=enum_values), nullable=False, default=RoleEnum.PATIENT)
    preferred_language = Column(String(20), nullable=False, default="english")
    is_active = Column(Boolean, nullable=False, default=True)
    # JTI of the currently valid refresh token (single-use rotation).
    refresh_jti = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone}, role={self.role})>"
