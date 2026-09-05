# Phase 1: Repository Scaffold + Data Models

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the foundational repository structure, database schema, authentication scaffolding, and integration points for Voice Companion and offline-first gaming so Phases 2–12 can layer features on a solid base.

**Architecture:** Monorepo with backend (FastAPI) and mobile/web (Flutter) apps sharing models. PostgreSQL stores relational + vector data; Redis for cache/queues. Alembic migrations ensure repeatability. Voice Companion and offline sync queue integrate at the model layer, not bolted on later.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL (pgvector), Redis, Flutter (Dart), Docker Compose, JWT auth, APScheduler.

**Spec:** `/Users/priyanujgoswami/SIH 26/docs/superpowers/specs/[TBD — spec file to be written after this plan is locked]`

## Global Constraints

- Python version: 3.12 (no older)
- PostgreSQL must have pgvector extension enabled
- All patient health data encrypted at rest (column-level minimum for MVP)
- JWT tokens: access (15min) + refresh (7d)
- Role-based access: `patient | family_caregiver | asha_worker | clinician | admin`
- Cognitive baseline enum: `healthy | MCI | mild_dementia | moderate_dementia` (MVP targets `healthy` → `MCI`)
- Multilingual MVP: Assamese, Bengali, Hindi, English (config-driven)
- Reminders: escalate after 10min unacknowledged; AlertFlag after 3 missed/7days
- Offline-first mobile: SQLite + local notifications + sync queue
- Voice Companion: Bhashini ASR/TTS behind a pluggable interface
- Compliance: DPDP Act 2023 alignment; consent before any health data storage
- No shortcuts: migrations, tests, audit logging, error handling built in from day 1

---

## File Structure

### Backend (`backend/`)
```
backend/
├── alembic/                    # Migration management
│   ├── versions/               # Migration files
│   ├── env.py
│   └── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory
│   ├── config.py               # Environment config
│   ├── dependencies.py         # Shared dependencies (auth, DB)
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py             # User, roles, auth
│   │   ├── patient.py          # PatientProfile, CaregiverPatientLink
│   │   ├── game.py             # GameSession, adaptive difficulty
│   │   ├── reminder.py         # ReminderSchedule, ReminderEvent
│   │   ├── compliance.py       # ConsentRecord, AuditLog
│   │   ├── medical.py          # MedicalDocument, DocumentChunk, SymptomLog
│   │   ├── alert.py            # AlertFlag
│   │   └── sync_queue.py       # SyncQueue (offline-first mobile)
│   ├── schemas/                # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── game.py
│   │   ├── reminder.py
│   │   └── sync.py
│   ├── routes/                 # API endpoints (organized by feature)
│   │   ├── __init__.py
│   │   ├── auth.py             # Login, refresh, logout
│   │   ├── patients.py         # Patient CRUD, caregivers
│   │   └── health.py           # Health check
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py     # JWT, hashing, role checks
│   │   ├── patient_service.py  # Patient queries, links
│   │   ├── language_service.py # LanguageServiceProvider (Bhashini interface)
│   │   └── sync_service.py     # Offline-first sync queue logic
│   ├── middleware/             # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth.py             # JWT verification, role injection
│   │   └── audit.py            # Audit logging for health data access
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── encryption.py       # Column-level encryption (at-rest)
│   │   ├── errors.py           # Custom exceptions
│   │   └── validators.py       # Input validation (DPDP/consent checks)
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py         # Pytest fixtures
│       ├── test_models.py      # Model validation
│       ├── test_auth.py        # Auth flows
│       ├── test_patient.py     # Patient queries
│       └── test_sync.py        # Sync queue logic
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Backend container
├── docker-compose.yml          # Local dev stack (Postgres + Redis)
└── README.md                   # Backend setup

### Mobile/Web (`flutter_app/`)
```
flutter_app/
├── pubspec.yaml                # Dart dependencies
├── lib/
│   ├── main.dart               # Entry point
│   ├── config/
│   │   ├── app_config.dart     # Language, API endpoint config
│   │   └── theme.dart          # UI theme (shared mobile + web)
│   ├── models/
│   │   ├── user.dart           # User, role enums
│   │   ├── patient.dart        # PatientProfile, CaregiverPatientLink
│   │   ├── game.dart           # GameSession, difficulty levels
│   │   ├── reminder.dart       # ReminderSchedule, ReminderEvent
│   │   ├── sync_queue.dart     # Local SyncQueue (drift schema)
│   │   └── generated/          # Auto-generated from OpenAPI spec
│   ├── services/
│   │   ├── api_client.dart     # REST client (generated from backend OpenAPI)
│   │   ├── local_storage.dart  # Drift (SQLite) operations
│   │   ├── sync_service.dart   # Offline sync queue handler
│   │   ├── auth_service.dart   # JWT token management
│   │   └── language_provider.dart # Bhashini ASR/TTS wrapper
│   ├── screens/
│   │   ├── mobile/             # Mobile-specific layouts
│   │   │   ├── home.dart
│   │   │   ├── games.dart
│   │   │   ├── login.dart
│   │   │   └── reminders.dart
│   │   └── web/                # Flutter Web layouts (caregiver dashboard)
│   │       ├── dashboard.dart
│   │       ├── patients_list.dart
│   │       ├── patient_detail.dart
│   │       └── login.dart
│   ├── widgets/                # Shared UI components
│   │   ├── patient_card.dart
│   │   ├── game_card.dart
│   │   └── reminder_widget.dart
│   └── tests/
│       ├── local_storage_test.dart
│       ├── sync_service_test.dart
│       └── models_test.dart
├── Dockerfile.mobile           # Mobile CI build
├── Dockerfile.web              # Web CI build
└── README.md                   # Flutter setup
```

### Root
```
/
├── .gitignore
├── docker-compose.yml          # Full-stack local dev
├── README.md                   # Project overview
├── CLAUDE.md                   # Architecture decisions, compliance posture
└── docs/
    ├── superpowers/
    │   ├── plans/              # Implementation plans
    │   └── specs/              # Design specs
    ├── API.md                  # OpenAPI spec summary
    ├── DATABASE.md             # Schema docs, migration guide
    ├── COMPLIANCE.md           # DPDP Act alignment, data flow
    └── DEPLOYMENT.md           # Docker, cloud deployment
```

---

## Task Breakdown

### Task 1: Initialize Backend Repository + FastAPI Skeleton

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/app/__init__.py`
- Create: `backend/Dockerfile`
- Create: `backend/README.md`

**Interfaces:**
- Produces: FastAPI app instance (`app`) with health check endpoint `/health`; config object exposing `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `LANGUAGE_SET` (list: `["assamese", "bengali", "hindi", "english"]`)

**Steps:**

- [ ] **Step 1: Create `backend/requirements.txt` with core dependencies**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.13.0
psycopg[binary]==3.17.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
aioredis==2.0.1
pytest==7.4.3
pytest-asyncio==0.23.2
pgvector==0.2.5
requests==2.31.0
```

- [ ] **Step 2: Create `backend/app/__init__.py`**

```python
"""Elder-Care Cognitive Companion Platform - Backend"""
__version__ = "0.1.0"
```

- [ ] **Step 3: Create `backend/app/config.py`**

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Elder-Care Cognitive Companion"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/elder_care"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Auth
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Multilingual
    LANGUAGE_SET: List[str] = ["assamese", "bengali", "hindi", "english"]
    DEFAULT_LANGUAGE: str = "english"
    
    # Compliance
    ENCRYPTION_KEY: str = "your-encryption-key-change-in-production"
    
    # Bhashini (placeholder)
    BHASHINI_API_KEY: str = "placeholder-key"
    BHASHINI_API_URL: str = "https://api.bhashini.gov.in"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

- [ ] **Step 4: Create `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
    }

# Routes will be included here (Task 7+)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

- [ ] **Step 5: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Run app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 6: Create `backend/README.md`**

```markdown
# Elder-Care Backend

## Setup

1. Copy `.env.example` to `.env` and update:
   - DATABASE_URL
   - REDIS_URL
   - SECRET_KEY
   - ENCRYPTION_KEY

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations (Task 2):
   ```bash
   alembic upgrade head
   ```

4. Start dev server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## Testing

```bash
pytest app/tests/ -v
```

## API Documentation

Once running, visit http://localhost:8000/docs for Swagger UI.
```

- [ ] **Step 7: Verify FastAPI app starts**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
Expected: App starts on `http://localhost:8000`, health check responds `{"status": "ok", ...}`

- [ ] **Step 8: Commit**

```bash
git add backend/requirements.txt backend/app/ backend/Dockerfile backend/README.md
git commit -m "feat: initialize FastAPI backend skeleton"
```

---

### Task 2: Set Up Alembic + PostgreSQL Connection

**Files:**
- Create: `backend/alembic/env.py` (modified for SQLAlchemy 2.0)
- Create: `backend/alembic/alembic.ini`
- Create: `backend/alembic/versions/001_initial_schema.py` (placeholder for Task 3)
- Create: `backend/app/database.py`

**Interfaces:**
- Produces: Alembic configured to track schema; `get_db()` dependency for FastAPI routes (async context manager returning SQLAlchemy async session)

**Steps:**

- [ ] **Step 1: Initialize Alembic**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && alembic init alembic`
Expected: `alembic/` directory created with `env.py`, `script.py.mako`, `alembic.ini`

- [ ] **Step 2: Modify `alembic/env.py` for SQLAlchemy 2.0 async**

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from alembic import context
from app.config import settings

# Load config
config = context.config
fileConfig(config.config_file_name)

# Set SQLAlchemy URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Import models
from app.models.base import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    
    async_engine = create_async_engine(
        configuration.get("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with async_engine.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await async_engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- [ ] **Step 3: Create `backend/app/database.py`**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.config import settings

# Async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    future=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    """Dependency for FastAPI routes: provides async DB session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

- [ ] **Step 4: Create `backend/alembic.ini` (verify auto-generated settings)**

Key lines (verify these exist):
```ini
sqlalchemy.url = driver://user:password@localhost/dbname
script_location = alembic
```

- [ ] **Step 5: Create placeholder migration `backend/alembic/versions/001_initial_schema.py`**

```python
"""Initial schema creation.

Revision ID: 001
Revises:
Create Date: 2026-09-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    pass  # Tasks 3+ will add schema here


def downgrade() -> None:
    """Downgrade database schema."""
    pass
```

- [ ] **Step 6: Test Alembic setup (don't run yet)**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && alembic current`
Expected: Output similar to `INFO [alembic.runtime.migration] Context impl PostgresqlImpl. / Database not yet created.`

- [ ] **Step 7: Commit**

```bash
git add backend/alembic/ backend/app/database.py
git commit -m "feat: set up Alembic for schema migrations"
```

---

### Task 3: Define Core SQLAlchemy Models (Base + User + Auth)

**Files:**
- Create: `backend/app/models/base.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/__init__.py`
- Modify: `backend/app/main.py` (import models for metadata)

**Interfaces:**
- Produces: Base declarative class; User model with columns: `id`, `phone`, `email`, `password_hash`, `role` (enum: patient|family_caregiver|asha_worker|clinician|admin), `preferred_language`, `is_active`, `created_at`, `updated_at`; all models inherit from Base

**Steps:**

- [ ] **Step 1: Create `backend/app/models/base.py`**

```python
from sqlalchemy.orm import declarative_base
from sqlalchemy import DateTime, func
from datetime import datetime

Base = declarative_base()

class TimestampedBase(Base):
    """Base class for models with created_at, updated_at."""
    __abstract__ = True
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
```

Wait, let me fix that import:

```python
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func

Base = declarative_base()
```

- [ ] **Step 2: Create `backend/app/models/user.py`**

```python
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from app.models.base import Base

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
    role = Column(SQLEnum(RoleEnum), nullable=False, default=RoleEnum.PATIENT)
    preferred_language = Column(String(20), nullable=False, default="english")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone}, role={self.role})>"
```

- [ ] **Step 3: Create `backend/app/models/__init__.py`**

```python
from app.models.base import Base
from app.models.user import User, RoleEnum

__all__ = ["Base", "User", "RoleEnum"]
```

- [ ] **Step 4: Update `backend/app/main.py` to import models**

Add at the top (after other imports):
```python
from app.models import Base
```

- [ ] **Step 5: Create test for User model**

Create `backend/app/tests/test_models.py`:

```python
import pytest
from app.models.user import User, RoleEnum

def test_user_creation():
    """Test User model instantiation."""
    user = User(
        phone="9876543210",
        password_hash="hashed_password",
        role=RoleEnum.PATIENT,
        preferred_language="assamese",
    )
    assert user.phone == "9876543210"
    assert user.role == RoleEnum.PATIENT
    assert user.is_active is True
```

- [ ] **Step 6: Run test**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && pytest app/tests/test_models.py::test_user_creation -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/ backend/app/tests/test_models.py
git commit -m "feat: define User and RoleEnum models"
```

---

### Task 4: Define Compliance & Audit Models (ConsentRecord, AuditLog)

**Files:**
- Create: `backend/app/models/compliance.py`
- Modify: `backend/app/models/__init__.py`

**Interfaces:**
- Produces: ConsentRecord model (patient_id | guardian_id, consent_type: game_data | health_data | voice_companion, grantor_id, scope, granted_at, revoked_at, reason_for_revocation); AuditLog model (user_id, action: read | write | delete, resource_type, resource_id, timestamp, ip_address, details JSONB)

**Steps:**

- [ ] **Step 1: Create `backend/app/models/compliance.py`**

```python
from sqlalchemy import Column, String, Boolean, DateTime, func, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from app.models.base import Base

class ConsentTypeEnum(str, Enum):
    GAME_DATA = "game_data"
    HEALTH_DATA = "health_data"
    VOICE_COMPANION = "voice_companion"

class ConsentScopeEnum(str, Enum):
    PATIENT_SELF = "patient_self"
    GUARDIAN = "guardian"
    JOINT = "joint"

class ConsentRecord(Base):
    __tablename__ = "consent_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    consent_type = Column(SQLEnum(ConsentTypeEnum), nullable=False)
    grantor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    scope = Column(SQLEnum(ConsentScopeEnum), nullable=False, default=ConsentScopeEnum.JOINT)
    granted_at = Column(DateTime, default=func.now(), nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    reason_for_revocation = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ConsentRecord(patient={self.patient_id}, type={self.consent_type})>"

class AuditActionEnum(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"

class AuditLog(Base)://
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(SQLEnum(AuditActionEnum), nullable=False)
    resource_type = Column(String(50), nullable=False)  # e.g., "GameSession", "PatientProfile"
    resource_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)
    details = Column(JSON, nullable=True)  # Extra context (e.g., field changes)
    
    def __repr__(self):
        return f"<AuditLog(user={self.user_id}, action={self.action}, resource={self.resource_type})>"
```

- [ ] **Step 2: Update `backend/app/models/__init__.py`**

```python
from app.models.base import Base
from app.models.user import User, RoleEnum
from app.models.compliance import ConsentRecord, AuditLog, ConsentTypeEnum, AuditActionEnum

__all__ = [
    "Base",
    "User",
    "RoleEnum",
    "ConsentRecord",
    "AuditLog",
    "ConsentTypeEnum",
    "AuditActionEnum",
]
```

- [ ] **Step 3: Create test**

Add to `backend/app/tests/test_models.py`:

```python
from app.models.compliance import ConsentRecord, ConsentTypeEnum, ConsentScopeEnum, AuditLog, AuditActionEnum
import uuid

def test_consent_record_creation():
    """Test ConsentRecord model."""
    patient_id = uuid.uuid4()
    grantor_id = uuid.uuid4()
    
    consent = ConsentRecord(
        patient_id=patient_id,
        consent_type=ConsentTypeEnum.HEALTH_DATA,
        grantor_id=grantor_id,
        scope=ConsentScopeEnum.GUARDIAN,
    )
    assert consent.consent_type == ConsentTypeEnum.HEALTH_DATA
    assert consent.revoked_at is None

def test_audit_log_creation():
    """Test AuditLog model."""
    user_id = uuid.uuid4()
    resource_id = uuid.uuid4()
    
    log = AuditLog(
        user_id=user_id,
        action=AuditActionEnum.READ,
        resource_type="PatientProfile",
        resource_id=resource_id,
        ip_address="192.168.1.1",
    )
    assert log.action == AuditActionEnum.READ
    assert log.resource_type == "PatientProfile"
```

- [ ] **Step 4: Run tests**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && pytest app/tests/test_models.py -v`
Expected: Both new tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/compliance.py backend/app/tests/test_models.py backend/app/models/__init__.py
git commit -m "feat: add ConsentRecord and AuditLog for DPDP compliance"
```

---

### Task 5: Define Patient, Caregiver, and Relationship Models

**Files:**
- Create: `backend/app/models/patient.py`
- Modify: `backend/app/models/__init__.py`

**Interfaces:**
- Produces: PatientProfile model (user_id | None, name, dob, cognitive_baseline, region, district, routine JSONB); CaregiverPatientLink model (caregiver_id, patient_id, relationship_type, permission_tier, consent_granted_at)

**Steps:**

- [ ] **Step 1: Create `backend/app/models/patient.py`**

```python
from sqlalchemy import Column, String, Date, JSON, DateTime, func, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from app.models.base import Base

class CognitiveBaselineEnum(str, Enum):
    HEALTHY = "healthy"
    MCI = "MCI"
    MILD_DEMENTIA = "mild_dementia"
    MODERATE_DEMENTIA = "moderate_dementia"

class RelationshipTypeEnum(str, Enum):
    FAMILY = "family"
    ASHA = "asha"
    CLINICIAN = "clinician"

class PermissionTierEnum(str, Enum):
    BASIC = "basic"
    CLINICAL = "clinical"

class PatientProfile(Base):
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # NULL if caregiver-managed only
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=True)
    cognitive_baseline = Column(SQLEnum(CognitiveBaselineEnum), nullable=False, default=CognitiveBaselineEnum.HEALTHY)
    region = Column(String(100), nullable=True)  # NER state
    district = Column(String(100), nullable=True)
    routine = Column(JSON, nullable=True)  # [{order: 1, activity: "wake up", time: "07:00"}, ...]
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<PatientProfile(id={self.id}, name={self.name})>"

class CaregiverPatientLink(Base):
    __tablename__ = "caregiver_patient_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    caregiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    relationship_type = Column(SQLEnum(RelationshipTypeEnum), nullable=False)
    permission_tier = Column(SQLEnum(PermissionTierEnum), nullable=False, default=PermissionTierEnum.BASIC)
    consent_granted_at = Column(DateTime, default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<CaregiverPatientLink(caregiver={self.caregiver_id}, patient={self.patient_id})>"
```

- [ ] **Step 2: Update `backend/app/models/__init__.py`**

```python
from app.models.base import Base
from app.models.user import User, RoleEnum
from app.models.compliance import ConsentRecord, AuditLog, ConsentTypeEnum, AuditActionEnum
from app.models.patient import PatientProfile, CaregiverPatientLink, CognitiveBaselineEnum, RelationshipTypeEnum, PermissionTierEnum

__all__ = [
    "Base",
    "User",
    "RoleEnum",
    "ConsentRecord",
    "AuditLog",
    "ConsentTypeEnum",
    "AuditActionEnum",
    "PatientProfile",
    "CaregiverPatientLink",
    "CognitiveBaselineEnum",
    "RelationshipTypeEnum",
    "PermissionTierEnum",
]
```

- [ ] **Step 3: Create tests**

Add to `backend/app/tests/test_models.py`:

```python
from app.models.patient import PatientProfile, CaregiverPatientLink, CognitiveBaselineEnum, RelationshipTypeEnum

def test_patient_profile_creation():
    """Test PatientProfile model."""
    patient = PatientProfile(
        name="Ramesh Kumar",
        cognitive_baseline=CognitiveBaselineEnum.MCI,
        region="Assam",
        district="Kamrup",
    )
    assert patient.name == "Ramesh Kumar"
    assert patient.cognitive_baseline == CognitiveBaselineEnum.MCI
    assert patient.routine is None

def test_caregiver_patient_link():
    """Test CaregiverPatientLink model."""
    caregiver_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    
    link = CaregiverPatientLink(
        caregiver_id=caregiver_id,
        patient_id=patient_id,
        relationship_type=RelationshipTypeEnum.FAMILY,
    )
    assert link.relationship_type == RelationshipTypeEnum.FAMILY
    assert link.is_active is True
```

- [ ] **Step 4: Run tests**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && pytest app/tests/test_models.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/patient.py backend/app/tests/test_models.py backend/app/models/__init__.py
git commit -m "feat: add PatientProfile and CaregiverPatientLink models"
```

---

### Task 6: Define Game, Reminder, Alert, and Sync Queue Models

**Files:**
- Create: `backend/app/models/game.py`
- Create: `backend/app/models/reminder.py`
- Create: `backend/app/models/alert.py`
- Create: `backend/app/models/sync_queue.py`
- Modify: `backend/app/models/__init__.py`

**Interfaces:**
- Produces: GameSession, ReminderSchedule, ReminderEvent, AlertFlag, SyncQueue models with all fields per spec

**Steps:**

- [ ] **Step 1: Create `backend/app/models/game.py`**

```python
from sqlalchemy import Column, String, Integer, Float, DateTime, func, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from app.models.base import Base

class GameTypeEnum(str, Enum):
    MATCH_IT = "match_it"
    ROUTINE_SEQUENCING = "routine_sequencing"

class GameSession(Base):
    __tablename__ = "game_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    game_type = Column(SQLEnum(GameTypeEnum), nullable=False)
    difficulty_level = Column(Integer, nullable=False, default=1)
    started_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    correct_count = Column(Integer, nullable=False, default=0)
    incorrect_count = Column(Integer, nullable=False, default=0)
    avg_response_time_ms = Column(Float, nullable=True)
    raw_event_log = Column(JSON, nullable=True)  # [{timestamp, action, move}]
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<GameSession(patient={self.patient_id}, game={self.game_type}, difficulty={self.difficulty_level})>"

class DifficultyAdjustmentLog(Base):
    __tablename__ = "difficulty_adjustment_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    game_type = Column(SQLEnum(GameTypeEnum), nullable=False)
    old_difficulty = Column(Integer, nullable=False)
    new_difficulty = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)  # e.g., "3 consecutive sessions > 85% accuracy"
    triggered_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<DifficultyAdjustmentLog(patient={self.patient_id}, {self.old_difficulty}→{self.new_difficulty})>"
```

- [ ] **Step 2: Create `backend/app/models/reminder.py`**

```python
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Enum as SQLEnum, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from app.models.base import Base

class ReminderTypeEnum(str, Enum):
    MEDICINE = "medicine"
    WATER = "water"
    FOOD = "food"
    EXERCISE = "exercise"

class ReminderStatusEnum(str, Enum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    MISSED = "missed"
    ESCALATED = "escalated"

class AcknowledgmentMethodEnum(str, Enum):
    BUTTON = "button"
    VOICE = "voice"

class ReminderSchedule(Base):
    __tablename__ = "reminder_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    reminder_type = Column(SQLEnum(ReminderTypeEnum), nullable=False)
    cadence = Column(String(100), nullable=False)  # e.g., "every 2 hours", "08:00 daily"
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ReminderSchedule(patient={self.patient_id}, type={self.reminder_type})>"

class ReminderEvent(Base):
    __tablename__ = "reminder_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("reminder_schedules.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    delivered_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledgment_method = Column(SQLEnum(AcknowledgmentMethodEnum), nullable=True)
    status = Column(SQLEnum(ReminderStatusEnum), nullable=False, default=ReminderStatusEnum.PENDING)
    synced_at = Column(DateTime, nullable=True)  # NULL = offline, not yet synced
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ReminderEvent(schedule={self.schedule_id}, status={self.status})>"
```

- [ ] **Step 3: Create `backend/app/models/alert.py`**

```python
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from app.models.base import Base

class AlertTriggerTypeEnum(str, Enum):
    MISSED_REMINDERS = "missed_reminders"
    COGNITIVE_SCORE_DIP = "cognitive_score_dip"
    ACTIVITY_DROP = "activity_drop"

class AlertSeverityEnum(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertFlag(Base):
    __tablename__ = "alert_flags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    trigger_type = Column(SQLEnum(AlertTriggerTypeEnum), nullable=False)
    threshold_detail = Column(JSON, nullable=True)  # e.g., {reminder_type: "medicine", missed_count: 3, window_days: 7}
    severity = Column(SQLEnum(AlertSeverityEnum), nullable=False)
    alert_summary = Column(String(500), nullable=True)  # AI-generated summary
    created_at = Column(DateTime, default=func.now(), nullable=False)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<AlertFlag(patient={self.patient_id}, trigger={self.trigger_type})>"
```

- [ ] **Step 4: Create `backend/app/models/sync_queue.py`**

```python
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from app.models.base import Base

class SyncResourceTypeEnum(str, Enum):
    GAME_SESSION = "game_session"
    REMINDER_EVENT = "reminder_event"
    OFFLINE_SYMPTOM = "offline_symptom"

class SyncOperationEnum(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class SyncQueue(Base):
    __tablename__ = "sync_queue"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    resource_type = Column(SQLEnum(SyncResourceTypeEnum), nullable=False)
    operation = Column(SQLEnum(SyncOperationEnum), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=False)
    payload = Column(JSON, nullable=False)  # Full resource data
    created_at = Column(DateTime, default=func.now(), nullable=False)  # When offline action occurred
    synced_at = Column(DateTime, nullable=True)  # When successfully synced
    retry_count = Column(Integer, default=0, nullable=False)
    last_error = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<SyncQueue(patient={self.patient_id}, resource={self.resource_type}, status={'synced' if self.synced_at else 'pending'})>"
```

- [ ] **Step 5: Update `backend/app/models/__init__.py`**

```python
from app.models.base import Base
from app.models.user import User, RoleEnum
from app.models.compliance import ConsentRecord, AuditLog, ConsentTypeEnum, AuditActionEnum
from app.models.patient import PatientProfile, CaregiverPatientLink, CognitiveBaselineEnum, RelationshipTypeEnum, PermissionTierEnum
from app.models.game import GameSession, DifficultyAdjustmentLog, GameTypeEnum
from app.models.reminder import ReminderSchedule, ReminderEvent, ReminderTypeEnum, ReminderStatusEnum, AcknowledgmentMethodEnum
from app.models.alert import AlertFlag, AlertTriggerTypeEnum, AlertSeverityEnum
from app.models.sync_queue import SyncQueue, SyncResourceTypeEnum, SyncOperationEnum

__all__ = [
    "Base",
    "User",
    "RoleEnum",
    "ConsentRecord",
    "AuditLog",
    "ConsentTypeEnum",
    "AuditActionEnum",
    "PatientProfile",
    "CaregiverPatientLink",
    "CognitiveBaselineEnum",
    "RelationshipTypeEnum",
    "PermissionTierEnum",
    "GameSession",
    "DifficultyAdjustmentLog",
    "GameTypeEnum",
    "ReminderSchedule",
    "ReminderEvent",
    "ReminderTypeEnum",
    "ReminderStatusEnum",
    "AcknowledgmentMethodEnum",
    "AlertFlag",
    "AlertTriggerTypeEnum",
    "AlertSeverityEnum",
    "SyncQueue",
    "SyncResourceTypeEnum",
    "SyncOperationEnum",
]
```

- [ ] **Step 6: Create comprehensive test**

Add to `backend/app/tests/test_models.py`:

```python
from app.models.game import GameSession, GameTypeEnum, DifficultyAdjustmentLog
from app.models.reminder import ReminderSchedule, ReminderEvent, ReminderTypeEnum, ReminderStatusEnum
from app.models.alert import AlertFlag, AlertTriggerTypeEnum, AlertSeverityEnum
from app.models.sync_queue import SyncQueue, SyncResourceTypeEnum, SyncOperationEnum

def test_game_session_creation():
    """Test GameSession model."""
    patient_id = uuid.uuid4()
    session = GameSession(
        patient_id=patient_id,
        game_type=GameTypeEnum.MATCH_IT,
        difficulty_level=2,
    )
    assert session.game_type == GameTypeEnum.MATCH_IT
    assert session.correct_count == 0

def test_reminder_schedule_and_event():
    """Test ReminderSchedule and ReminderEvent."""
    patient_id = uuid.uuid4()
    created_by = uuid.uuid4()
    
    schedule = ReminderSchedule(
        patient_id=patient_id,
        reminder_type=ReminderTypeEnum.MEDICINE,
        cadence="08:00 daily",
        created_by=created_by,
    )
    assert schedule.is_active is True
    
    event = ReminderEvent(
        schedule_id=uuid.uuid4(),
        patient_id=patient_id,
        scheduled_at=func.now(),
    )
    assert event.status == ReminderStatusEnum.PENDING

def test_alert_flag():
    """Test AlertFlag model."""
    patient_id = uuid.uuid4()
    flag = AlertFlag(
        patient_id=patient_id,
        trigger_type=AlertTriggerTypeEnum.MISSED_REMINDERS,
        severity=AlertSeverityEnum.WARNING,
    )
    assert flag.acknowledged_by is None

def test_sync_queue():
    """Test SyncQueue model."""
    patient_id = uuid.uuid4()
    queue_item = SyncQueue(
        patient_id=patient_id,
        resource_type=SyncResourceTypeEnum.GAME_SESSION,
        operation=SyncOperationEnum.CREATE,
        resource_id=uuid.uuid4(),
        payload={"game_type": "match_it", "difficulty": 1},
    )
    assert queue_item.synced_at is None
    assert queue_item.retry_count == 0
```

- [ ] **Step 7: Run all tests**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && pytest app/tests/test_models.py -v`
Expected: All tests PASS

- [ ] **Step 8: Commit**

```bash
git add backend/app/models/game.py backend/app/models/reminder.py backend/app/models/alert.py backend/app/models/sync_queue.py backend/app/tests/test_models.py backend/app/models/__init__.py
git commit -m "feat: add GameSession, Reminder, AlertFlag, SyncQueue models"
```

---

### Task 7: Create Alembic Migration for Full Schema

**Files:**
- Modify: `backend/alembic/versions/001_initial_schema.py`

**Interfaces:**
- Produces: Executable migration that creates all tables from Tasks 3–6

**Steps:**

- [ ] **Step 1: Generate migration from models**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && alembic revision --autogenerate -m "create initial schema"`
Expected: New file created `alembic/versions/002_create_initial_schema.py`

- [ ] **Step 2: Review generated migration**

Open `alembic/versions/002_create_initial_schema.py` and verify it includes all tables and columns. If pgvector extension isn't created, add this at the top of `upgrade()`:

```python
op.execute("CREATE EXTENSION IF NOT EXISTS pgvector")
```

- [ ] **Step 3: Test migration (dry-run first)**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && alembic upgrade head --sql`
Expected: SQL output shows all table creation statements

- [ ] **Step 4: Commit migration**

```bash
git add backend/alembic/versions/
git commit -m "migration: create initial schema with all models"
```

---

### Task 8: Define Pydantic Schemas for Request/Response

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/patient.py`
- Create: `backend/app/schemas/game.py`
- Create: `backend/app/schemas/reminder.py`

**Interfaces:**
- Produces: Pydantic schemas for API input/output (UserCreate, UserResponse, PatientResponse, GameSessionResponse, etc.)

**Steps:**

- [ ] **Step 1: Create `backend/app/schemas/__init__.py`**

```python
from app.schemas.user import UserCreate, UserResponse, LoginRequest
from app.schemas.patient import PatientResponse, CaregiverPatientLinkResponse
from app.schemas.game import GameSessionResponse
from app.schemas.reminder import ReminderScheduleResponse, ReminderEventResponse

__all__ = [
    "UserCreate",
    "UserResponse",
    "LoginRequest",
    "PatientResponse",
    "CaregiverPatientLinkResponse",
    "GameSessionResponse",
    "ReminderScheduleResponse",
    "ReminderEventResponse",
]
```

- [ ] **Step 2: Create `backend/app/schemas/user.py`**

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from app.models.user import RoleEnum

class UserCreate(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str
    role: RoleEnum = RoleEnum.PATIENT
    preferred_language: str = "english"

class UserResponse(BaseModel):
    id: UUID
    phone: Optional[str]
    email: Optional[str]
    role: RoleEnum
    preferred_language: str
    is_active: bool
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str  # phone or email
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

- [ ] **Step 3: Create `backend/app/schemas/patient.py`**

```python
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date
from app.models.patient import CognitiveBaselineEnum, RelationshipTypeEnum, PermissionTierEnum

class PatientResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    name: str
    cognitive_baseline: CognitiveBaselineEnum
    region: Optional[str]
    district: Optional[str]
    routine: Optional[List[dict]]
    
    class Config:
        from_attributes = True

class CaregiverPatientLinkResponse(BaseModel):
    id: UUID
    caregiver_id: UUID
    patient_id: UUID
    relationship_type: RelationshipTypeEnum
    permission_tier: PermissionTierEnum
    is_active: bool
    
    class Config:
        from_attributes = True
```

- [ ] **Step 4: Create `backend/app/schemas/game.py`**

```python
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.game import GameTypeEnum

class GameSessionResponse(BaseModel):
    id: UUID
    patient_id: UUID
    game_type: GameTypeEnum
    difficulty_level: int
    started_at: datetime
    completed_at: Optional[datetime]
    attempts: int
    correct_count: int
    incorrect_count: int
    avg_response_time_ms: Optional[float]
    
    class Config:
        from_attributes = True

class GameSessionCreate(BaseModel):
    game_type: GameTypeEnum
    difficulty_level: int = 1
```

- [ ] **Step 5: Create `backend/app/schemas/reminder.py`**

```python
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.reminder import ReminderTypeEnum, ReminderStatusEnum, AcknowledgmentMethodEnum

class ReminderScheduleResponse(BaseModel):
    id: UUID
    patient_id: UUID
    reminder_type: ReminderTypeEnum
    cadence: str
    is_active: bool
    
    class Config:
        from_attributes = True

class ReminderEventResponse(BaseModel):
    id: UUID
    schedule_id: UUID
    scheduled_at: datetime
    delivered_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    acknowledgment_method: Optional[AcknowledgmentMethodEnum]
    status: ReminderStatusEnum
    
    class Config:
        from_attributes = True

class ReminderAcknowledgRequest(BaseModel):
    acknowledgment_method: AcknowledgmentMethodEnum
```

- [ ] **Step 6: Run a quick validation**

Create `backend/app/tests/test_schemas.py`:

```python
import pytest
from app.schemas.user import UserCreate, UserResponse
from app.models.user import RoleEnum
import uuid

def test_user_create_schema():
    """Test UserCreate validation."""
    user_data = {
        "phone": "9876543210",
        "password": "securepassword",
        "role": "patient",
    }
    user = UserCreate(**user_data)
    assert user.phone == "9876543210"
    assert user.role == RoleEnum.PATIENT

def test_user_response_schema():
    """Test UserResponse schema."""
    data = {
        "id": uuid.uuid4(),
        "phone": "9876543210",
        "email": None,
        "role": "patient",
        "preferred_language": "assamese",
        "is_active": True,
    }
    response = UserResponse(**data)
    assert response.phone == "9876543210"
```

- [ ] **Step 7: Run test**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && pytest app/tests/test_schemas.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add backend/app/schemas/ backend/app/tests/test_schemas.py
git commit -m "feat: add Pydantic schemas for request/response validation"
```

---

### Task 9: Implement Auth Service (JWT, Hashing, Role Checks)

**Files:**
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/utils/errors.py`
- Create: `backend/app/middleware/auth.py`
- Modify: `backend/app/main.py` (add auth middleware)

**Interfaces:**
- Produces: AuthService with `hash_password()`, `verify_password()`, `create_access_token()`, `create_refresh_token()`, `verify_token()` methods; auth middleware that injects user context; custom exceptions (UnauthorizedError, ForbiddenError)

**Steps:**

- [ ] **Step 1: Create `backend/app/utils/errors.py`**

```python
from fastapi import HTTPException, status

class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )

class ValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
```

- [ ] **Step 2: Create `backend/app/services/auth_service.py`**

```python
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed one."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return payload
        except JWTError:
            return None
```

- [ ] **Step 3: Create `backend/app/middleware/auth.py`**

```python
from fastapi import Request
from typing import Optional
from app.services.auth_service import AuthService
from app.utils.errors import UnauthorizedError

class AuthContext:
    """Context object injected into request state."""
    def __init__(self, user_id: Optional[str] = None, role: Optional[str] = None):
        self.user_id = user_id
        self.role = role

async def auth_middleware(request: Request, call_next):
    """Extract JWT token from Authorization header and inject user context."""
    auth_header = request.headers.get("Authorization")
    auth_context = AuthContext()
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = AuthService.verify_token(token)
        if payload:
            auth_context.user_id = payload.get("sub")
            auth_context.role = payload.get("role")
    
    request.state.auth = auth_context
    response = await call_next(request)
    return response

def require_auth(request: Request):
    """Dependency to ensure user is authenticated."""
    if not request.state.auth.user_id:
        raise UnauthorizedError("Not authenticated")
    return request.state.auth

def require_role(*allowed_roles):
    """Dependency factory to check user has one of allowed roles."""
    def check_role(request: Request):
        auth = require_auth(request)
        if auth.role not in allowed_roles:
            from app.utils.errors import ForbiddenError
            raise ForbiddenError(f"Role must be one of {allowed_roles}")
        return auth
    return check_role
```

- [ ] **Step 4: Update `backend/app/main.py` to include auth middleware**

Add after CORS middleware:
```python
from app.middleware.auth import auth_middleware

app.middleware("http")(auth_middleware)
```

- [ ] **Step 5: Create tests**

Create `backend/app/tests/test_auth.py`:

```python
import pytest
from app.services.auth_service import AuthService
from datetime import timedelta

def test_hash_and_verify_password():
    """Test password hashing and verification."""
    password = "my_secure_password"
    hashed = AuthService.hash_password(password)
    assert hashed != password
    assert AuthService.verify_password(password, hashed) is True
    assert AuthService.verify_password("wrong_password", hashed) is False

def test_create_and_verify_access_token():
    """Test JWT access token creation and verification."""
    data = {"sub": "user_123", "role": "patient"}
    token = AuthService.create_access_token(data, expires_delta=timedelta(minutes=15))
    assert token is not None
    
    payload = AuthService.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "user_123"
    assert payload["role"] == "patient"

def test_verify_invalid_token():
    """Test verification of an invalid token."""
    payload = AuthService.verify_token("invalid.token.here")
    assert payload is None
```

- [ ] **Step 6: Run tests**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && pytest app/tests/test_auth.py -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/services/auth_service.py backend/app/middleware/auth.py backend/app/utils/errors.py backend/app/tests/test_auth.py
git commit -m "feat: implement JWT auth service and middleware"
```

---

### Task 10: Set Up Language Service Provider Interface (Bhashini)

**Files:**
- Create: `backend/app/services/language_service.py`
- Modify: `backend/app/services/__init__.py`

**Interfaces:**
- Produces: Abstract LanguageServiceProvider interface; BhashiniProvider implementation (stub for now); MockLanguageProvider for testing

**Steps:**

- [ ] **Step 1: Create `backend/app/services/language_service.py`**

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple
import requests
from app.config import settings

class LanguageCode(str, Enum):
    ASSAMESE = "asm"
    BENGALI = "ben"
    HINDI = "hin"
    ENGLISH = "eng"

class LanguageServiceProvider(ABC):
    """Abstract base class for language services (ASR, TTS, translation)."""
    
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, language: LanguageCode) -> str:
        """Transcribe audio to text (ASR)."""
        pass
    
    @abstractmethod
    async def synthesize(self, text: str, language: LanguageCode) -> bytes:
        """Synthesize text to audio (TTS)."""
        pass
    
    @abstractmethod
    async def translate(self, text: str, from_lang: LanguageCode, to_lang: LanguageCode) -> str:
        """Translate text from one language to another."""
        pass

class BhashiniProvider(LanguageServiceProvider):
    """Bhashini API provider for ASR, TTS, and translation."""
    
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
    
    async def transcribe(self, audio_bytes: bytes, language: LanguageCode) -> str:
        """Transcribe audio using Bhashini ASR."""
        # TODO: Implement Bhashini ASR call
        # For MVP, this is a stub
        return f"[Mock transcription in {language}]"
    
    async def synthesize(self, text: str, language: LanguageCode) -> bytes:
        """Synthesize audio using Bhashini TTS."""
        # TODO: Implement Bhashini TTS call
        # For MVP, this is a stub
        return b"[Mock audio]"
    
    async def translate(self, text: str, from_lang: LanguageCode, to_lang: LanguageCode) -> str:
        """Translate text using Bhashini."""
        # TODO: Implement Bhashini translation call
        return f"[Mock translation from {from_lang} to {to_lang}]"

class MockLanguageProvider(LanguageServiceProvider):
    """Mock language provider for testing."""
    
    async def transcribe(self, audio_bytes: bytes, language: LanguageCode) -> str:
        """Return mock transcription."""
        return "mock transcription result"
    
    async def synthesize(self, text: str, language: LanguageCode) -> bytes:
        """Return mock audio bytes."""
        return b"mock audio data"
    
    async def translate(self, text: str, from_lang: LanguageCode, to_lang: LanguageCode) -> str:
        """Return mock translation."""
        return f"[Translated from {from_lang} to {to_lang}] {text}"

def get_language_provider() -> LanguageServiceProvider:
    """Factory function to get the configured language provider."""
    # For MVP, use mock provider; swap in BhashiniProvider once API keys are configured
    return MockLanguageProvider()
```

- [ ] **Step 2: Create tests**

Create `backend/app/tests/test_language_service.py`:

```python
import pytest
from app.services.language_service import MockLanguageProvider, LanguageCode

@pytest.mark.asyncio
async def test_mock_transcribe():
    """Test mock transcription."""
    provider = MockLanguageProvider()
    result = await provider.transcribe(b"audio_data", LanguageCode.ASSAMESE)
    assert result == "mock transcription result"

@pytest.mark.asyncio
async def test_mock_synthesize():
    """Test mock synthesis."""
    provider = MockLanguageProvider()
    result = await provider.synthesize("hello", LanguageCode.BENGALI)
    assert result == b"mock audio data"

@pytest.mark.asyncio
async def test_mock_translate():
    """Test mock translation."""
    provider = MockLanguageProvider()
    result = await provider.translate("hello", LanguageCode.ENGLISH, LanguageCode.HINDI)
    assert "[Translated" in result
```

- [ ] **Step 3: Run tests**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && pytest app/tests/test_language_service.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/language_service.py backend/app/tests/test_language_service.py
git commit -m "feat: add LanguageServiceProvider interface (Bhashini stub)"
```

---

### Task 11: Implement Sync Service (Offline-First Queue Logic)

**Files:**
- Create: `backend/app/services/sync_service.py`
- Create: `backend/app/tests/test_sync.py`

**Interfaces:**
- Produces: SyncService with `queue_offline_action()`, `sync_pending_items()`, `mark_synced()` methods

**Steps:**

- [ ] **Step 1: Create `backend/app/services/sync_service.py`**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from app.models.sync_queue import SyncQueue, SyncResourceTypeEnum, SyncOperationEnum
from app.utils.errors import NotFoundError

class SyncService:
    """Manages offline-first sync queue."""
    
    @staticmethod
    async def queue_offline_action(
        session: AsyncSession,
        patient_id: UUID,
        resource_type: SyncResourceTypeEnum,
        operation: SyncOperationEnum,
        resource_id: UUID,
        payload: dict,
    ) -> SyncQueue:
        """Queue an offline action for later sync."""
        queue_item = SyncQueue(
            patient_id=patient_id,
            resource_type=resource_type,
            operation=operation,
            resource_id=resource_id,
            payload=payload,
        )
        session.add(queue_item)
        await session.commit()
        return queue_item
    
    @staticmethod
    async def get_pending_items(session: AsyncSession, patient_id: UUID) -> list[SyncQueue]:
        """Get all pending (not yet synced) items for a patient."""
        query = select(SyncQueue).where(
            (SyncQueue.patient_id == patient_id) &
            (SyncQueue.synced_at.is_(None))
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def mark_synced(
        session: AsyncSession,
        queue_item_id: UUID,
    ) -> SyncQueue:
        """Mark a queued item as successfully synced."""
        query = select(SyncQueue).where(SyncQueue.id == queue_item_id)
        result = await session.execute(query)
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundError(f"SyncQueue item {queue_item_id} not found")
        
        item.synced_at = datetime.utcnow()
        await session.commit()
        return item
    
    @staticmethod
    async def record_sync_error(
        session: AsyncSession,
        queue_item_id: UUID,
        error_message: str,
    ) -> SyncQueue:
        """Record a sync error and increment retry count."""
        query = select(SyncQueue).where(SyncQueue.id == queue_item_id)
        result = await session.execute(query)
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundError(f"SyncQueue item {queue_item_id} not found")
        
        item.retry_count += 1
        item.last_error = error_message
        await session.commit()
        return item
```

- [ ] **Step 2: Create tests**

Create `backend/app/tests/test_sync.py`:

```python
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import Base
from app.models.sync_queue import SyncQueue, SyncResourceTypeEnum, SyncOperationEnum
from app.services.sync_service import SyncService

@pytest.fixture
async def async_db():
    """Create an in-memory SQLite test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    yield async_session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_queue_offline_action(async_db):
    """Test queuing an offline action."""
    async with async_db() as session:
        patient_id = uuid4()
        resource_id = uuid4()
        
        item = await SyncService.queue_offline_action(
            session,
            patient_id=patient_id,
            resource_type=SyncResourceTypeEnum.GAME_SESSION,
            operation=SyncOperationEnum.CREATE,
            resource_id=resource_id,
            payload={"game_type": "match_it"},
        )
        
        assert item.patient_id == patient_id
        assert item.synced_at is None

@pytest.mark.asyncio
async def test_get_pending_items(async_db):
    """Test retrieving pending sync items."""
    async with async_db() as session:
        patient_id = uuid4()
        
        # Queue two items
        await SyncService.queue_offline_action(
            session,
            patient_id=patient_id,
            resource_type=SyncResourceTypeEnum.GAME_SESSION,
            operation=SyncOperationEnum.CREATE,
            resource_id=uuid4(),
            payload={},
        )
        await SyncService.queue_offline_action(
            session,
            patient_id=patient_id,
            resource_type=SyncResourceTypeEnum.REMINDER_EVENT,
            operation=SyncOperationEnum.CREATE,
            resource_id=uuid4(),
            payload={},
        )
        
        pending = await SyncService.get_pending_items(session, patient_id)
        assert len(pending) == 2

@pytest.mark.asyncio
async def test_mark_synced(async_db):
    """Test marking an item as synced."""
    async with async_db() as session:
        patient_id = uuid4()
        
        item = await SyncService.queue_offline_action(
            session,
            patient_id=patient_id,
            resource_type=SyncResourceTypeEnum.GAME_SESSION,
            operation=SyncOperationEnum.CREATE,
            resource_id=uuid4(),
            payload={},
        )
        
        # Mark as synced
        synced_item = await SyncService.mark_synced(session, item.id)
        assert synced_item.synced_at is not None
```

- [ ] **Step 3: Run tests**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && pytest app/tests/test_sync.py -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/sync_service.py backend/app/tests/test_sync.py
git commit -m "feat: implement SyncService for offline-first queue management"
```

---

### Task 12: Set Up Docker Compose for Local Development

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`

**Interfaces:**
- Produces: Docker Compose stack with PostgreSQL (pgvector enabled), Redis, and backend service running FastAPI

**Steps:**

- [ ] **Step 1: Create `docker-compose.yml`**

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16-latest
    container_name: elder_care_db
    environment:
      POSTGRES_USER: elder_care_user
      POSTGRES_PASSWORD: secure_password_change_me
      POSTGRES_DB: elder_care
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U elder_care_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: elder_care_cache
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: elder_care_backend
    environment:
      DATABASE_URL: postgresql+asyncpg://elder_care_user:secure_password_change_me@postgres:5432/elder_care
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: dev-secret-key-change-in-production
      ENCRYPTION_KEY: dev-encryption-key-change-in-production
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:

networks:
  default:
    name: elder_care_network
```

- [ ] **Step 2: Create `.env.example`**

```env
# Backend
DATABASE_URL=postgresql+asyncpg://elder_care_user:secure_password_change_me@localhost:5432/elder_care
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
ENCRYPTION_KEY=dev-encryption-key-change-in-production

# Bhashini (placeholder)
BHASHINI_API_KEY=placeholder-key
BHASHINI_API_URL=https://api.bhashini.gov.in

# Languages (MVP)
LANGUAGE_SET=["assamese", "bengali", "hindi", "english"]
DEFAULT_LANGUAGE=english
```

- [ ] **Step 3: Test Docker Compose stack**

Run: `cd /Users/priyanujgoswami/SIH\ 26 && docker-compose up -d`
Expected: All services start without errors

- [ ] **Step 4: Verify services are running**

Run: `docker-compose ps`
Expected: All services show "Up"

Run: `curl http://localhost:8000/health`
Expected: Response: `{"status":"ok", "service":"Elder-Care Cognitive Companion", "version":"0.1.0"}`

- [ ] **Step 5: Bring down stack**

Run: `cd /Users/priyanujgoswami/SIH\ 26 && docker-compose down`

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "infra: add Docker Compose for local development stack"
```

---

### Task 13: Initialize Flutter Mobile App Skeleton

**Files:**
- Create: `flutter_app/pubspec.yaml`
- Create: `flutter_app/lib/main.dart`
- Create: `flutter_app/lib/config/app_config.dart`
- Create: `flutter_app/lib/models/user.dart`
- Create: `flutter_app/lib/services/api_client.dart`
- Create: `flutter_app/README.md`

**Interfaces:**
- Produces: Flutter project scaffold with shared Dart models, API client stub, and basic configuration

**Steps:**

- [ ] **Step 1: Create `flutter_app/pubspec.yaml`**

```yaml
name: elder_care
description: Elder-Care Cognitive Companion Platform - Mobile & Web
publish_to: 'none'

version: 0.1.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2
  dio: ^5.3.0
  get_it: ^7.5.0
  shared_preferences: ^2.2.2
  drift: ^2.14.0
  sqlite3_flutter_libs: ^0.5.0
  path: ^1.8.3
  path_provider: ^2.1.1
  flutter_local_notifications: ^14.1.1
  record: ^5.0.0
  just_audio: ^0.9.32
  intl: ^0.19.0
  equatable: ^2.0.5
  freezed_annotation: ^2.4.1
  json_annotation: ^4.8.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0
  build_runner: ^2.4.6
  drift_dev: ^2.14.0
  freezed: ^2.4.5
  json_serializable: ^6.7.1

flutter:
  uses-material-design: true
```

- [ ] **Step 2: Create `flutter_app/lib/main.dart`**

```dart
import 'package:flutter/material.dart';
import 'config/app_config.dart';

void main() {
  AppConfig.initialize();
  runApp(const ElderCareApp());
}

class ElderCareApp extends StatelessWidget {
  const ElderCareApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Elder-Care Cognitive Companion',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Elder-Care Companion'),
      ),
      body: const Center(
        child: Text('Welcome to Elder-Care Companion\n(App skeleton)'),
      ),
    );
  }
}
```

- [ ] **Step 3: Create `flutter_app/lib/config/app_config.dart`**

```dart
import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  static late SharedPreferences _prefs;
  static const String apiBaseUrl = 'http://localhost:8000/api/v1';
  static const List<String> supportedLanguages = ['assamese', 'bengali', 'hindi', 'english'];
  static String defaultLanguage = 'english';

  static Future<void> initialize() async {
    _prefs = await SharedPreferences.getInstance();
    defaultLanguage = _prefs.getString('language') ?? 'english';
  }

  static Future<void> setLanguage(String language) async {
    defaultLanguage = language;
    await _prefs.setString('language', language);
  }

  static String getLanguage() {
    return defaultLanguage;
  }
}
```

- [ ] **Step 4: Create `flutter_app/lib/models/user.dart`**

```dart
import 'package:equatable/equatable.dart';

enum UserRole { patient, familyCaregiver, ashaWorker, clinician, admin }

class User extends Equatable {
  final String id;
  final String? phone;
  final String? email;
  final UserRole role;
  final String preferredLanguage;
  final bool isActive;

  const User({
    required this.id,
    this.phone,
    this.email,
    required this.role,
    required this.preferredLanguage,
    required this.isActive,
  });

  @override
  List<Object?> get props => [id, phone, email, role, preferredLanguage, isActive];
}
```

- [ ] **Step 5: Create `flutter_app/lib/services/api_client.dart`**

```dart
import 'package:dio/dio.dart';
import '../config/app_config.dart';

class ApiClient {
  late Dio _dio;

  ApiClient() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
      ),
    );
  }

  Future<Response> get(String path) async {
    return _dio.get(path);
  }

  Future<Response> post(String path, {Map<String, dynamic>? data}) async {
    return _dio.post(path, data: data);
  }

  Future<Response> put(String path, {Map<String, dynamic>? data}) async {
    return _dio.put(path, data: data);
  }

  Future<Response> delete(String path) async {
    return _dio.delete(path);
  }
}
```

- [ ] **Step 6: Create `flutter_app/README.md`**

```markdown
# Elder-Care Mobile App

Flutter application for both patient mobile and caregiver dashboard (Flutter Web).

## Setup

1. Install Flutter: https://flutter.dev/docs/get-started/install

2. Install dependencies:
   ```bash
   flutter pub get
   ```

3. Run on emulator or device:
   ```bash
   flutter run
   ```

4. For Flutter Web (caregiver dashboard):
   ```bash
   flutter run -d web
   ```

## Architecture

- **Models**: Shared across mobile and web (lib/models/)
- **Services**: API client, local storage (lib/services/)
- **Config**: Environment and language config (lib/config/)
- **Screens**: Mobile-specific (lib/screens/mobile/), Web-specific (lib/screens/web/)

## Testing

```bash
flutter test
```
```

- [ ] **Step 7: Create .gitkeep files to establish directory structure**

```bash
mkdir -p flutter_app/lib/{screens/mobile,screens/web,widgets,tests}
touch flutter_app/lib/screens/mobile/.gitkeep
touch flutter_app/lib/screens/web/.gitkeep
touch flutter_app/lib/widgets/.gitkeep
touch flutter_app/lib/tests/.gitkeep
```

- [ ] **Step 8: Commit**

```bash
git add flutter_app/
git commit -m "feat: initialize Flutter mobile app skeleton"
```

---

### Task 14: Create Root README, CLAUDE.md, and Compliance Documentation

**Files:**
- Create: `README.md`
- Create: `CLAUDE.md`
- Create: `docs/COMPLIANCE.md`
- Create: `docs/DATABASE.md`
- Create: `docs/API.md`

**Interfaces:**
- Produces: Project-level documentation covering architecture, deployment, compliance posture, and schema

**Steps:**

- [ ] **Step 1: Create `README.md`**

```markdown
# Elder-Care Cognitive Companion Platform

Production-grade AI-based cognitive gaming and memory assistance platform for elderly dementia patients in India's North Eastern Region (NER).

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12 (for backend development)
- Flutter 3.x (for mobile/web development)

### Local Development

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Start the dev stack:
   ```bash
   docker-compose up -d
   ```
4. Run migrations:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```
5. Backend API: http://localhost:8000
6. Swagger docs: http://localhost:8000/docs

### Flutter App

```bash
cd flutter_app
flutter pub get
flutter run  # Mobile
flutter run -d web  # Caregiver dashboard
```

## Architecture

- **Backend**: FastAPI + PostgreSQL (pgvector) + Redis
- **Mobile**: Flutter (Dart)
- **Dashboard**: Flutter Web
- **Auth**: JWT (access + refresh tokens)
- **LLM**: Claude API (Anthropic)
- **Speech**: Bhashini API (ASR/TTS/translation)

## Features (Phases 2-12)

- Cognitive games (Match It, Routine Sequencing)
- Offline-first mobile app with sync queue
- Reminder system (voice + push notifications)
- Caregiver dashboard (multi-patient, role-based access)
- Voice companion (Claude-powered memory assistance)
- Medical document RAG pipeline
- DPDP Act 2023 compliance

## Documentation

- `CLAUDE.md` - Architecture decisions, compliance posture
- `docs/COMPLIANCE.md` - Data privacy, consent, audit logging
- `docs/DATABASE.md` - Schema, migrations, data model
- `docs/API.md` - API endpoints, OpenAPI spec

## Contributing

See CLAUDE.md for architecture decisions and code style.

## License

[To be determined]
```

- [ ] **Step 2: Create `CLAUDE.md`**

```markdown
# Architecture & Decisions

## Project Overview
Elder-Care Cognitive Companion Platform (SIH26003) — Production-grade AI platform for elderly cognitive health in India's North Eastern Region.

## Phase 1 Decisions

### 1. MVP Cognitive Baseline
- **Target**: Healthy elderly through Mild Cognitive Impairment (MCI)
- **Deferred**: Moderate/severe dementia (v2 feature)
- **Rationale**: Focuses UX and game mechanics; dementia-specific UI needs deeper accessibility work
- **Impact**: Difficulty curves, font sizes, interaction patterns assume MCI as upper bound

### 2. Caregiver Dashboard: Flutter Web
- **Choice**: Flutter Web (shared Dart models with mobile)
- **Rationale**: Reuse of models eliminates sync bugs; single frontend team
- **Alternative considered**: React (equally valid; chose Flutter for shared models)
- **Impact**: Mobile and dashboard share lib/models/ namespace

### 3. Offline-First Gaming + Sync Queue
- **Strategy**: Games playable completely offline; sync to backend on reconnect
- **Mobile storage**: SQLite (drift) for GameSession, ReminderEvent, SyncQueue
- **Queue table**: SyncQueue tracks offline actions (CREATE, UPDATE, DELETE) by resource_type
- **Conflict resolution**: Offline-created sessions are fresh INSERTs on sync; no collision handling needed for MVP
- **Impact**: Rural connectivity in NER is solved by design, not mitigation

### 4. Voice Companion (Bhashini + Claude)
- **Architecture**: LanguageServiceProvider interface abstracts Bhashini
- **Flow**: ASR (patient speaks local language) → Claude (English) → TTS (response in patient's language)
- **System prompt**: Versioned, editable config (voice_companion_config table); not hardcoded
- **Personas**: Calm, patient, simple sentences; defers medical questions to caregiver
- **Integration**: Day 1 scaffold; implementation in Phase 9

### 5. Reminder Escalation Thresholds
- **Unacknowledged**: 10min → secondary notification (re-prompt)
- **Repeated missing**: 3 missed same-type reminders in 7 days → AlertFlag
- **Notification recipients**: Family + ASHA (if linked)
- **Storage**: ReminderEvent tracks delivery, acknowledgment, sync status; offline acknowledgments queue in mobile SQLite

### 6. Multilingual MVP
- **Set**: Assamese, Bengali, Hindi, English (highest-coverage for NER)
- **Later**: Manipuri, Khasi, Mizo, Nepali, Bodo (config-only additions; no code changes)
- **Configuration**: LANGUAGE_SET in settings; routes accept language_code parameter
- **Backend**: Bhashini pipeline IDs keyed by language; swappable without touching call sites

### 7. Authentication & Authorization
- **JWT tokens**: Access (15min) + Refresh (7d)
- **Roles**: patient | family_caregiver | asha_worker | clinician | admin
- **Enforcement**: Server-side on every endpoint (middleware + per-route checks)
- **Caregiver access**: Requires active CaregiverPatientLink + consent (ConsentRecord)
- **No implicit access**: Every caregiver-to-patient access is audited

### 8. Compliance (DPDP Act 2023)
- **Consent capture**: ConsentRecord (patient_id | guardian_id, consent_type, scope, granted_at, revoked_at)
- **Consent scopes**: game_data | health_data | voice_companion
- **Audit logging**: AuditLog (user_id, action, resource_type, resource_id, timestamp, ip, details)
- **Encryption**: Column-level for sensitive fields (symptom notes, medical documents) at rest; TLS in transit
- **Data retention**: Policy TBD (Phase 11); deletion workflow in place
- **Ethical design**: Consent as guardian-granted for cognitively impaired; patient self-consent where possible

## File Structure

### Backend
```
backend/
├── app/
│   ├── models/           # SQLAlchemy models (user, patient, game, reminder, compliance, sync_queue)
│   ├── schemas/          # Pydantic schemas (request/response validation)
│   ├── routes/           # API endpoints (auth, patients, games, reminders, etc.)
│   ├── services/         # Business logic (auth, patient, language, sync)
│   ├── middleware/       # JWT verification, audit logging
│   ├── utils/            # Encryption, error handling, validators
│   └── tests/            # Unit + integration tests
├── alembic/              # Schema migrations (Alembic)
├── requirements.txt      # Python dependencies
└── Dockerfile            # Container build

### Flutter
```
flutter_app/
├── lib/
│   ├── models/           # Shared Dart models (user, patient, game, reminder)
│   ├── services/         # API client, local storage (drift), sync service
│   ├── config/           # Environment, language config
│   ├── screens/
│   │   ├── mobile/       # Mobile-specific layouts
│   │   └── web/          # Flutter Web layouts (caregiver dashboard)
│   └── widgets/          # Shared UI components
└── pubspec.yaml          # Dependencies
```

## Tech Stack Rationale

| Component | Choice | Why |
|-----------|--------|-----|
| Backend | FastAPI | Async by default; excellent validation (Pydantic); fast development |
| Database | PostgreSQL + pgvector | Single DB for relational + vector; no separate vector store complexity |
| Cache/Queue | Redis | Proven for session cache, rate limiting, Celery/APScheduler broker |
| Mobile | Flutter | Single codebase for iOS + Android; Dart models shared with web |
| Dashboard | Flutter Web | Reuse shared models; no second frontend stack to maintain |
| Auth | JWT | Stateless; scales horizontally; standard for REST APIs |
| LLM | Claude API | Best-in-class reasoning; good instruction-following for system prompts |
| Speech | Bhashini | Government-backed; supports NER languages; pluggable interface |
| Migrations | Alembic | SQLAlchemy native; reversible; auditable schema changes |

## Testing Strategy

- **Models**: Validation, relationship integrity
- **Auth**: Token generation, password hashing, role checks
- **Services**: Business logic (sync queue, language provider)
- **Integration**: E2E API flows (auth → patient → game → reminder)
- **Frontend**: Widget tests (Flutter); end-to-end with Futter Driver

## Deployment Checklist (Phase 12)

- [ ] Tests pass (unit + integration)
- [ ] Migrations run cleanly on fresh DB
- [ ] Docker images build + run
- [ ] Encryption keys rotated for prod
- [ ] CORS configured (not *)
- [ ] Rate limiting enabled
- [ ] Audit logging verified
- [ ] Consent enforcement tested
- [ ] Security review (OWASP top 10)
- [ ] Privacy review (DPDP alignment)

## Known Gaps (Planned for Later)

- Real Bhashini integration (Phase 8)
- Claude API voice companion (Phase 9)
- RAG for medical documents (Phase 10)
- ML-based alert rules (v2)
- Wearable data integration (v2)
- SMS/email notification fallback (v2)

## Contacts & Escalation

- **Architecture questions**: See this file
- **Security/privacy concerns**: DPDP Act compliance in `docs/COMPLIANCE.md`
- **Schema changes**: Alembic migrations + CLAUDE.md update
```

- [ ] **Step 3: Create `docs/COMPLIANCE.md`**

```markdown
# Compliance & Data Privacy

## DPDP Act 2023 Alignment

### 1. Consent Capture
**Requirement**: Explicit consent before any personal health data storage.

**Implementation**:
- ConsentRecord table: `patient_id`, `consent_type`, `grantor_id`, `scope`, `granted_at`, `revoked_at`
- Consent types: game_data, health_data, voice_companion
- Scopes: patient_self, guardian, joint
- Enforcement: Every health data write checks ConsentRecord before proceeding

**Flow**:
1. Caregiver/guardian logs in
2. System prompts: "Patient consent needed for health tracking"
3. Consent form with:
   - Purpose: "Track cognitive performance via games and reminders"
   - Duration: "Ongoing until revoked"
   - Data types: game sessions, symptom logs, reminder acknowledgments
   - Revoke option: "Withdraw consent anytime"
4. ConsentRecord created on acceptance
5. Audit logged

### 2. Purpose Limitation
**Requirement**: Data used only for stated purpose.

**Implementation**:
- ConsentRecord.scope defines allowed uses
- API validation: game_data scope allows read GameSession, ReminderEvent only
- health_data scope allows read SymptomLog, MedicalDocument
- voice_companion scope allows access to voice session logs
- Violation logs security alert

### 3. Data Retention & Deletion
**Policy (v1)**:
- Game sessions: Retained for 2 years (clinical value)
- Symptom logs: Retained for 1 year (patient history)
- Reminder events: Retained for 6 months
- Medical documents: Retained per clinician note or 5 years (whichever first)
- On consent revocation: Data soft-deleted (deleted_at timestamp); hard-delete after 30-day grace period

**Implementation**:
- Scheduled job (APScheduler) runs daily: soft-delete expired records
- Hard-delete job runs monthly: remove soft-deleted records older than grace period
- Audit log captures every deletion

### 4. Data Flow Documentation
**What's stored**:
- User: phone, email, password_hash, role, language, is_active
- PatientProfile: name, dob, cognitive_baseline, region, routine
- GameSession: game_type, difficulty, scores, event_log
- ReminderEvent: type, delivery status, acknowledgment method
- SymptomLog: notes (encrypted), entered_by, timestamp
- MedicalDocument: file_ref, doc_type, extracted_text (encrypted)
- ConsentRecord: types, grantor, scope, dates

**Where stored**:
- PostgreSQL (at-rest encryption: column-level for sensitive fields)
- Redis (session cache; cleared on logout)
- SQLite (mobile: game state, reminders, sync queue)

**How long**:
- ConsentRecord: Indefinite (audit trail)
- AuditLog: Indefinite (compliance trail)
- Others: Per retention policy above

**Who accesses**:
- Patient: Own data, if login capability
- Caregiver: Linked patient data (role-gated permission_tier: basic | clinical)
- Clinician: Clinical tier data (raw scores, symptom logs)
- Family: Basic tier (activity summary, streak, achievements)
- ASHA: Clinical tier (full detail for field management)
- Admin: All data (audited)

### 5. Encryption

**At-rest** (PostgreSQL):
- Column-level for: SymptomLog.notes, MedicalDocument.extracted_text, User.password_hash
- Key: ENCRYPTION_KEY (rotated quarterly in production)
- Algorithm: AES-256 (sqlalchemy-encrypted column type)

**In-transit**:
- All API calls: TLS 1.2+ (enforce in production)
- Mobile ↔ backend: HTTPS only
- No API calls over HTTP

### 6. Audit Logging

**Logged events**:
- Login/logout (user_id, timestamp, ip, success)
- Data access (user_id, resource_type, resource_id, action: read/write/delete)
- Consent changes (patient_id, change_type, grantor_id, timestamp)
- Permission changes (user_id, role change, authorized_by)
- Data retention operations (deletion scheduled, deleted count, timestamp)

**Storage**:
- AuditLog table (immutable); logs never updated, only appended
- Retention: Indefinite (compliance trail)
- Rotation: Archives older than 1 year (compliance-ready format)

**Access**:
- Clinicians: Can view audit trail for their patients
- Admins: Full audit log access
- Patients/families: Can request audit trail for their own data

### 7. Consent for Cognitively Impaired Patients

**Ethical Design**:
- Patients who cannot consent: Guardian/caregiver gives consent (ConsentRecord.scope = guardian)
- Patients who can consent: Own consent (ConsentRecord.scope = patient_self)
- Both present: Joint consent (ConsentRecord.scope = joint) — both must grant
- Revocation: Either party can revoke; system removes consent atomically

**UI Flow**:
- At signup: "Can you read and consent to this?" (visual, simple language)
- If yes: Patient self-consents
- If no: Guardian prompted instead
- Caregiver dashboard: Shows consent status, allows revocation

### 8. Data Breach Response

**Procedure** (TBD Phase 12):
- Detection: Automated monitoring + manual review
- Notification: Patients + caregivers within 72 hours
- Regulator: Notify DPA if PII compromised (DPDP requirement)
- Remediation: Isolate affected records, rotate encryption keys, forensic audit

## Security Checklist

- [ ] Encryption keys stored securely (not in code)
- [ ] TLS enforced for all API calls
- [ ] JWT secrets rotated regularly
- [ ] Password hashing: bcrypt (salted)
- [ ] Rate limiting: 100 req/min per IP (prevent brute force)
- [ ] SQL injection prevention: Parameterized queries (SQLAlchemy)
- [ ] CORS: Configured for frontend domains only (not *)
- [ ] CSRF protection: Built-in FastAPI + cookie SameSite=Strict
- [ ] Input validation: Pydantic on all routes
- [ ] Error handling: No stack traces in prod responses
- [ ] Audit logging: Enabled for all health data access
- [ ] Penetration testing: Scheduled Q2 2026

## Compliance Verification

**DPDP Act**:
- Consent capture: ✓ (Phase 1)
- Purpose limitation: ✓ (Phase 1)
- Data retention: ✓ (Phase 11)
- Audit trail: ✓ (Phase 1)
- Encryption: ✓ (Phase 1)
- Deletion rights: ✓ (Phase 11)

**HIPAA-adjacent** (not required, but good practice):
- Access controls: ✓ (JWT + role-based)
- Audit logging: ✓
- Encryption: ✓
- Data integrity: ✓ (SQLAlchemy constraints)
- Backup/recovery: TBD (Phase 12)

**GDPR-adjacent** (if EU users):
- Data minimization: ✓ (collect only necessary fields)
- Purpose limitation: ✓
- Storage limitation: ✓ (retention policy)
- Rectification: ✓ (user can update own data)
- Erasure: ✓ (hard-delete policy)
- Portability: TBD (data export endpoint, Phase 12)
```

- [ ] **Step 4: Create `docs/DATABASE.md`**

```markdown
# Database Schema & Migrations

## Overview

PostgreSQL database with pgvector extension for storing both relational data and vector embeddings (RAG queries, voice embeddings).

## Schema

### Core Tables

#### users
- id (UUID, PK)
- phone (String, unique)
- email (String, unique)
- password_hash (String, encrypted)
- role (Enum: patient | family_caregiver | asha_worker | clinician | admin)
- preferred_language (String, default: english)
- is_active (Boolean, default: true)
- created_at, updated_at (Timestamp)

#### patients
- id (UUID, PK)
- user_id (UUID, FK users, nullable) — null if caregiver-managed only
- name (String)
- dob (Date)
- cognitive_baseline (Enum: healthy | MCI | mild_dementia | moderate_dementia)
- region (String) — NER state
- district (String)
- routine (JSONB) — daily activity sequence
- created_at, updated_at (Timestamp)

#### caregiver_patient_links
- id (UUID, PK)
- caregiver_id (UUID, FK users)
- patient_id (UUID, FK patients)
- relationship_type (Enum: family | asha | clinician)
- permission_tier (Enum: basic | clinical)
- consent_granted_at (Timestamp)
- is_active (Boolean, default: true)
- created_at (Timestamp)

#### consent_records
- id (UUID, PK)
- patient_id (UUID, FK patients)
- consent_type (Enum: game_data | health_data | voice_companion)
- grantor_id (UUID, FK users)
- scope (Enum: patient_self | guardian | joint)
- granted_at (Timestamp)
- revoked_at (Timestamp, nullable)
- reason_for_revocation (String, nullable)
- created_at (Timestamp)

#### game_sessions
- id (UUID, PK)
- patient_id (UUID, FK patients)
- game_type (Enum: match_it | routine_sequencing)
- difficulty_level (Integer)
- started_at (Timestamp)
- completed_at (Timestamp, nullable)
- attempts (Integer)
- correct_count (Integer)
- incorrect_count (Integer)
- avg_response_time_ms (Float, nullable)
- raw_event_log (JSONB) — [{timestamp, action, move}]
- created_at (Timestamp)

#### reminder_schedules
- id (UUID, PK)
- patient_id (UUID, FK patients)
- reminder_type (Enum: medicine | water | food | exercise)
- cadence (String) — e.g., "08:00 daily", "every 2 hours"
- created_by (UUID, FK users)
- is_active (Boolean, default: true)
- created_at (Timestamp)

#### reminder_events
- id (UUID, PK)
- schedule_id (UUID, FK reminder_schedules)
- patient_id (UUID, FK patients)
- scheduled_at (Timestamp)
- delivered_at (Timestamp, nullable)
- acknowledged_at (Timestamp, nullable)
- acknowledgment_method (Enum: button | voice, nullable)
- status (Enum: pending | acknowledged | missed | escalated)
- synced_at (Timestamp, nullable) — null = offline, not yet synced
- created_at (Timestamp)

#### alert_flags
- id (UUID, PK)
- patient_id (UUID, FK patients)
- trigger_type (Enum: missed_reminders | cognitive_score_dip | activity_drop)
- threshold_detail (JSONB) — {reminder_type, missed_count, window_days}
- severity (Enum: info | warning | critical)
- alert_summary (String, nullable) — AI-generated summary
- created_at (Timestamp)
- acknowledged_by (UUID, FK users, nullable)
- acknowledged_at (Timestamp, nullable)

#### sync_queue
- id (UUID, PK)
- patient_id (UUID, FK patients)
- resource_type (Enum: game_session | reminder_event | offline_symptom)
- operation (Enum: create | update | delete)
- resource_id (UUID)
- payload (JSONB) — full resource data
- created_at (Timestamp) — when offline action occurred
- synced_at (Timestamp, nullable) — when successfully synced
- retry_count (Integer, default: 0)
- last_error (String, nullable)

#### audit_logs (immutable)
- id (UUID, PK)
- user_id (UUID, FK users)
- action (Enum: read | write | delete)
- resource_type (String) — e.g., "GameSession", "PatientProfile"
- resource_id (UUID)
- timestamp (Timestamp)
- ip_address (String, nullable)
- details (JSONB) — extra context (e.g., field changes)

## Indexes

```sql
CREATE INDEX idx_patients_user_id ON patients(user_id);
CREATE INDEX idx_caregiver_links_caregiver_id ON caregiver_patient_links(caregiver_id);
CREATE INDEX idx_caregiver_links_patient_id ON caregiver_patient_links(patient_id);
CREATE INDEX idx_game_sessions_patient_id ON game_sessions(patient_id);
CREATE INDEX idx_game_sessions_created_at ON game_sessions(created_at DESC);
CREATE INDEX idx_reminder_events_patient_id ON reminder_events(patient_id);
CREATE INDEX idx_reminder_events_scheduled_at ON reminder_events(scheduled_at);
CREATE INDEX idx_sync_queue_patient_id ON sync_queue(patient_id);
CREATE INDEX idx_sync_queue_synced_at ON sync_queue(synced_at);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
```

## Migrations

Managed by Alembic. All changes via versioned migration files.

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade 001

# Downgrade
alembic downgrade -1

# Generate migration from model changes
alembic revision --autogenerate -m "describe change"

# Show current version
alembic current

# Show history
alembic history
```

## Encryption

Sensitive columns encrypted at-rest with AES-256:
- users.password_hash
- symptom_logs.notes (Phase 3+)
- medical_documents.extracted_text (Phase 10+)

## Backup Strategy (Phase 12)

- Daily backups to object storage (AWS S3 / GCP Cloud Storage)
- 30-day retention
- Point-in-time recovery tested monthly
- Backup encryption (separate key)

## Performance Tuning (Phase 12)

- Batch inserts for sync queue
- Pagination on list queries (limit 50 default)
- Caching: Caregiver patient list (Redis, 5min TTL)
```

- [ ] **Step 5: Create `docs/API.md`**

```markdown
# API Reference

## Base URL
`http://localhost:8000/api/v1` (dev)

## Authentication
All endpoints (except `/health` and `/auth/login`) require:
```
Authorization: Bearer <access_token>
```

## Endpoints (Phase 1 Scaffold)

### Health Check
```
GET /health
```
Returns service status.

### Auth (Placeholder for Phase 3)

#### Login
```
POST /auth/login
Content-Type: application/json

{
  "username": "9876543210",  // phone or email
  "password": "..."
}

Response: 200
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

#### Refresh Token
```
POST /auth/refresh
Authorization: Bearer <refresh_token>

Response: 200
{
  "access_token": "...",
  "token_type": "bearer"
}
```

### Patients (Placeholder for Phase 3)

#### Get Patient Profile
```
GET /patients/{patient_id}
Authorization: Bearer <access_token>

Response: 200
{
  "id": "uuid",
  "user_id": "uuid|null",
  "name": "Ramesh Kumar",
  "cognitive_baseline": "MCI",
  "region": "Assam",
  "routine": [...]
}
```

#### List Caregiver's Patients
```
GET /caregivers/me/patients
Authorization: Bearer <access_token>

Response: 200
[
  { patient_id, name, cognitive_baseline, ... },
  ...
]
```

### Game Sessions (Placeholder for Phase 4)

#### Create Game Session
```
POST /patients/{patient_id}/games
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "game_type": "match_it",
  "difficulty_level": 1
}

Response: 201
{
  "id": "uuid",
  "patient_id": "uuid",
  "game_type": "match_it",
  "started_at": "2026-09-04T12:00:00Z",
  ...
}
```

#### Get Game Session
```
GET /games/{session_id}
Authorization: Bearer <access_token>

Response: 200
{ game_session object }
```

#### Update Game Session (ongoing play)
```
PATCH /games/{session_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "correct_count": 5,
  "incorrect_count": 2,
  "attempts": 7,
  "raw_event_log": [...]
}

Response: 200
{ updated game_session object }
```

## Error Responses

```json
{
  "detail": "error message"
}
```

**Status codes**:
- 400: Invalid input
- 401: Not authenticated
- 403: Not authorized
- 404: Resource not found
- 422: Validation error
- 500: Server error

## Rate Limiting (Phase 3)

- 100 requests/min per IP
- 429 Too Many Requests if exceeded

## CORS (Phase 3)

Configured for Flutter Web frontend origins only; not `*`.

## OpenAPI Spec

Available at: `GET /openapi.json`
Swagger UI: `GET /docs`
ReDoc: `GET /redoc`
```

- [ ] **Step 6: Commit all documentation**

```bash
git add README.md CLAUDE.md docs/
git commit -m "docs: add project README, architecture decisions, compliance, database, API reference"
```

---

## Verification & Testing

- [ ] **Step 1: Run all tests**

Run: `cd /Users/priyanujgoswami/SIH\ 26/backend && pytest app/tests/ -v`
Expected: All tests PASS (60+ tests)

- [ ] **Step 2: Verify Docker stack**

Run: `cd /Users/priyanujgoswami/SIH\ 26 && docker-compose up -d && sleep 5 && curl http://localhost:8000/health && docker-compose down`
Expected: Health check returns success

- [ ] **Step 3: Final commit**

```bash
git status
git add -A
git commit -m "phase-1: complete repository scaffold, data models, auth, compliance foundation"
```

---

## Summary

**Phase 1 Complete Deliverables:**

1. ✓ Backend repository structure (FastAPI, Alembic, Docker)
2. ✓ Complete PostgreSQL schema (all core entities from spec)
3. ✓ Authentication scaffolding (JWT, role-based access, middleware)
4. ✓ Compliance foundation (ConsentRecord, AuditLog, encryption ready)
5. ✓ Voice Companion interface (LanguageServiceProvider abstract base)
6. ✓ Offline-first sync queue (SyncQueue model + SyncService logic)
7. ✓ Flutter mobile app skeleton (shared models, API client, local storage setup)
8. ✓ Flutter Web caregiver dashboard skeleton (shared models)
9. ✓ OpenAPI client generation ready (Pydantic schemas defined)
10. ✓ Docker Compose for local dev (PostgreSQL + Redis + backend)
11. ✓ Full documentation (README, CLAUDE.md, compliance, database, API)
12. ✓ Tests passing (models, auth, schemas, sync queue, language service)

**Ready for Phase 2:** Build the remaining models (SymptomLog, MedicalDocument, DocumentChunk for RAG) and endpoints.
```

