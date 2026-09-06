# Deployment — SIH26003 Elder-Care Companion (2026-09-06)

## Status
- All 12 phases implemented (CLAUDE.md reconciliation).
- 130 pytest pass + 1 skipped (pypdf env); 21/21 standalone service tests.
- CI: pytest + alembic + smoke_e2e (Postgres 16) + flutter pub/get/analyze.
- Production posture: secret/CORS refusal (config.py:149-158), rate limit (Redis+fallback), Fernet encryption, audit logs.

## Pre-deploy checklist (must complete before flip to production)
1. Generate real SECRET_KEY (>=24 chars) and ENCRYPTION_KEY (>=16 chars).
2. Set CORS_ORIGINS to real origins (not *); ENVIRONMENT=production.
3. Add OPENROUTER_API_KEY / BHASHINI_API_KEY / ANTHROPIC_API_KEY (opt-in).
4. Provision managed Postgres (pgvector) + run `alembic upgrade head`.
5. Set TLS 1.2+ in front (load balancer / reverse proxy).
6. Configure real notification channel (SMS/FCM/APNs) beyond console.
7. Clean build artifacts (mobile/build, .dart_tool; backend/.venv) and refresh graph (`graphify update .`).

## Run
```
docker-compose up -d  # dev shape; swap to managed DB + TLS for prod
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Source of truth: CLAUDE.md (reconciled 2026-09-06); supersedes all older .md files.
