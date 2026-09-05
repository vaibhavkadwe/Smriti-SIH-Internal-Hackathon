"""Tests for RetentionService — DPDP retention windows + consent grace deletion."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.models.all_models import (
    AuditActionEnum,
    AuditLog,
    ConsentRecord,
    ConsentTypeEnum,
    GameSession,
    GameTypeEnum,
    MedicalDocument,
    PatientProfile,
    ReminderEvent,
    ReminderSchedule,
    ReminderStatusEnum,
    ReminderTypeEnum,
    SymptomLog,
    SyncQueue,
    SyncOperationEnum,
    SyncResourceTypeEnum,
)
from app.models.user import RoleEnum, User
from app.services.retention_service import RetentionService


async def _patient_and_users(db):
    u = User(phone=f"+91{uuid.uuid4().int % 10**10}", password_hash="x", role=RoleEnum.PATIENT)
    db.add(u)
    await db.flush()
    p = PatientProfile(user_id=u.id, name="Retention", region="assam")
    db.add(p)
    await db.flush()
    return u, p


@pytest.mark.asyncio
async def test_purges_expired_keeps_recent(db_session):
    now = datetime.now(timezone.utc)
    user, patient = await _patient_and_users(db_session)
    pid = patient.id  # snapshot: maintenance commits and expires ORM attrs

    # Old (3y) vs recent (1d) game sessions
    old = GameSession(patient_id=patient.id, game_type=GameTypeEnum.MATCH_IT,
                      completed_at=now - timedelta(days=365 * 3))
    recent = GameSession(patient_id=patient.id, game_type=GameTypeEnum.MATCH_IT,
                         completed_at=now - timedelta(days=1))
    db_session.add_all([old, recent])
    # Old (2y) vs recent symptom logs
    db_session.add(SymptomLog(patient_id=patient.id, entered_by=user.id,
                              notes="old note", created_at=now - timedelta(days=730)))
    db_session.add(SymptomLog(patient_id=patient.id, entered_by=user.id,
                              notes="recent note", created_at=now))
    # Old (7mo) reminder event
    db_session.add(ReminderEvent(patient_id=patient.id, schedule_id=uuid.uuid4(),
                                 scheduled_at=now - timedelta(days=210),
                                 status=ReminderStatusEnum.ACKNOWLEDGED))
    # Synced queue row from 10 days ago + one pending
    db_session.add(SyncQueue(patient_id=patient.id,
                             resource_type=SyncResourceTypeEnum.GAME_SESSION,
                             operation=SyncOperationEnum.CREATE, resource_id=uuid.uuid4(),
                             payload={}, synced_at=now - timedelta(days=10)))
    db_session.add(SyncQueue(patient_id=patient.id,
                             resource_type=SyncResourceTypeEnum.GAME_SESSION,
                             operation=SyncOperationEnum.CREATE, resource_id=uuid.uuid4(),
                             payload={}, synced_at=None))
    await db_session.flush()

    counts = await RetentionService.run_maintenance(db_session, now=now)

    assert counts["game_sessions"] == 1
    assert counts["symptom_logs"] == 1
    assert counts["reminder_events"] == 1
    assert counts["sync_queue"] == 1  # only the 10-day-old synced row
    # Only the RECENT game session survives
    remaining = (
        await db_session.execute(select(GameSession).where(GameSession.patient_id == pid))
    ).scalars().all()
    assert len(remaining) == 1
    # Normalize timezone so both naive (fresh SQLite read) and aware
    # (identity-mapped instance) values compare cleanly.
    completed = remaining[0].completed_at
    if completed is not None and completed.tzinfo is None:
        completed = completed.replace(tzinfo=timezone.utc)
    assert completed >= now - timedelta(days=2)


@pytest.mark.asyncio
async def test_old_sessions_and_docs_purged_with_chunks(db_session):
    now = datetime.now(timezone.utc)
    user, patient = await _patient_and_users(db_session)

    old_doc = MedicalDocument(patient_id=patient.id, uploaded_by=user.id,
                              file_ref="old.pdf", doc_type="report",
                              created_at=now - timedelta(days=365 * 6))
    db_session.add(old_doc)
    await db_session.flush()
    from app.models.all_models import DocumentChunk

    db_session.add(DocumentChunk(document_id=old_doc.id, patient_id=patient.id,
                                 chunk_text="old chunk"))
    await db_session.flush()

    counts = await RetentionService.run_maintenance(db_session, now=now)
    assert counts["medical_documents"] == 1
    assert counts["document_chunks"] == 1


@pytest.mark.asyncio
async def test_revoked_consent_hard_deleted_after_grace(db_session):
    now = datetime.now(timezone.utc)
    user, patient = await _patient_and_users(db_session)

    expired = ConsentRecord(patient_id=patient.id, consent_type=ConsentTypeEnum.PATIENT_SELF,
                            scope="all", granted_at=now - timedelta(days=60),
                            revoked_at=now - timedelta(days=45))
    within_grace = ConsentRecord(patient_id=patient.id, consent_type=ConsentTypeEnum.PATIENT_SELF,
                                 scope="all", granted_at=now - timedelta(days=10),
                                 revoked_at=now - timedelta(days=5))
    active = ConsentRecord(patient_id=patient.id, consent_type=ConsentTypeEnum.PATIENT_SELF,
                           scope="all", granted_at=now)
    db_session.add_all([expired, within_grace, active])
    await db_session.flush()

    counts = await RetentionService.run_maintenance(db_session, now=now)
    assert counts["consent_records"] == 1  # only the expired one


@pytest.mark.asyncio
async def test_audit_logs_never_purged(db_session):
    now = datetime.now(timezone.utc)
    user, patient = await _patient_and_users(db_session)
    old_log = AuditLog(user_id=user.id, action=AuditActionEnum.READ,
                       resource_type="patient_profile", resource_id=patient.id,
                       timestamp=now - timedelta(days=3650))
    db_session.add(old_log)
    await db_session.flush()
    log_id = old_log.id  # snapshot before the maintenance commit expires attrs

    counts = await RetentionService.run_maintenance(db_session, now=now)
    assert "audit_logs" not in counts  # immutable trail, never deleted
    remaining = await db_session.get(AuditLog, log_id)
    assert remaining is not None


@pytest.mark.asyncio
async def test_maintenance_idempotent(db_session):
    now = datetime.now(timezone.utc)
    user, patient = await _patient_and_users(db_session)
    db_session.add(GameSession(patient_id=patient.id, game_type=GameTypeEnum.MATCH_IT,
                               completed_at=now - timedelta(days=365 * 3)))
    await db_session.flush()
    first = await RetentionService.run_maintenance(db_session, now=now)
    second = await RetentionService.run_maintenance(db_session, now=now)
    assert first["game_sessions"] == 1
    assert second["game_sessions"] == 0
