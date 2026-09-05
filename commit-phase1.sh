#!/bin/bash
cd "/Users/priyanujgoswami/SIH 26/.claude/worktrees/phase-1-scaffold"

# Initialize git if needed
git init

# Add all files
git add -A

# Commit
git commit -m "feat: phase-1 task-1 foundation - FastAPI skeleton, database layer, core models

- FastAPI app with health check endpoint
- Pydantic settings configuration
- SQLAlchemy async engine and session factory
- Core models: User (with RoleEnum), PatientProfile, CaregiverPatientLink
- Compliance models: ConsentRecord, AuditLog (DPDP Act alignment)
- Game models: GameSession, DifficultyAdjustmentLog
- Reminder models: ReminderSchedule, ReminderEvent
- Alert models: AlertFlag
- SyncQueue model (offline-first mobile)
- Auth service: JWT token generation, password hashing, verification
- Docker container definition

All models include proper enums, relationships, timestamps, and DPDP compliance fields.
Ready for Alembic migration in Task 2."

# Show result
git log --oneline -1
