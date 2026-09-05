# Deployment Guide — Elder-Care Cognitive Companion (SIH26003)

> Reconciled with the repository on 2026-09-04. Earlier versions of this file
> claimed "all 12 phases implemented and verified (7/7 tests)" — that did not
> match the repo. Actual state: backend through Phase 10, implemented and
> tested; phases 11–12 and Flutter compile-verification still open (see
> `PHASE_1_STATUS.md`).

## Architecture overview

| Component | Tech | Location | Status |
|---|---|---|---|
| Backend API | FastAPI (async) + SQLAlchemy 2.0 | `backend/` | ✅ Implemented |
| Database | PostgreSQL 15+ with pgvector | `docker-compose.yml` | Migration `0001` exists, **not yet applied to a live PG** |
| Cache/Queue | Redis | `docker-compose.yml` | Configured in env; not required for tests |
| Patient app | Flutter (mobile) | `mobile/` | Wired to API; **uncompiled (no SDK here)** |
| Caregiver dashboard | Flutter Web | `dashboard/` | Same caveat |
| Speech (ASR/TTS/NMT) | Bhashini | `backend/app/services/language_service.py` | Code complete; needs `BHASHINI_API_KEY`/`USER_ID` |
| LLM (companion + RAG answers) | Anthropic Claude | `backend/app/services/llm_client.py` | Code complete; needs `ANTHROPIC_API_KEY` |
| Compliance | Consent + AuditLog + AES-256 | `backend/app/` | Built; Phase 11 (retention jobs, read-audit middleware) pending |

## Local development

```bash
# 1. Infrastructure (Postgres + Redis) — or use your own Postgres
docker compose up -d

# 2. Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env      # defaults work locally; add real keys when available

# 3. Schema
alembic upgrade head          # migration 0001: 15 tables, 17 enum types

# 4. Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Verify
curl http://localhost:8000/health
```

Interactive API docs: **http://localhost:8000/docs** (Swagger) and
**http://localhost:8000/redoc** — the OpenAPI schema is served at
`/api/v1/openapi.json` (50 routes total: 49 under `/api/v1` + `/health`).

### Running tests (no database required)

```bash
cd backend
.venv/bin/python -m pytest app/tests tests -q   # 56 passed (unit + API-level)
.venv/bin/python test_phase2_services.py        # 20 standalone checks
```

Both suites use an in-memory SQLite DB. The Alembic migration has been
validated only via offline SQL rendering — apply it to a real Postgres and
run an end-to-end smoke before calling the DB path verified.

## Environment variables

Full documented set in `.env.example`. The important ones:

```bash
# Database / cache
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/eldercare
REDIS_URL=redis://redis:6379/0

# Security — generate real values, never ship the placeholders
SECRET_KEY=openssl rand -hex 32          # HS256 signing
ENCRYPTION_KEY=CHANGE_ME_32_BYTE_KEY     # AES-256 at-rest (column-level)
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Speech — Bhashini (Phase 8). Provider: auto | bhashini | mock
LANGUAGE_SERVICE_PROVIDER=auto           # auto = real when creds set, else mock
BHASHINI_API_KEY=
BHASHINI_USER_ID=
BHASHINI_ENDPOINT=https://dhruva-api.bhashini.gov.in/services/inference/pipeline

# LLM — Anthropic Claude (Phases 9/10)
ANTHROPIC_API_KEY=                       # or CLAUDE_API_KEY (legacy alias)
ANTHROPIC_VERSION=2023-06-01
CLAUDE_MODEL=claude-3-haiku-20240307
CLAUDE_MAX_TOKENS=300
LLM_AUTO_FALLBACK=true                   # canned reply instead of error when key absent
```

## Production deployment

### Backend

**Docker:**
```bash
cd backend
docker build -t eldercare-backend .
docker run -p 8000:8000 --env-file .env eldercare-backend
```

**PaaS** (Railway, Render, Fly.io, AWS ECS): set the env vars above, start
command `uvicorn app.main:app --host 0.0.0.0`.

### Database

Managed Postgres with pgvector (Neon, Supabase, RDS). After provisioning:

```bash
psql "$DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS vector;"
cd backend && alembic upgrade head
```

### Mobile app

```bash
cd mobile
flutter create .          # platform folders were never generated
flutter pub get
dart run build_runner build --delete-conflicting-outputs   # drift codegen
flutter run               # --dart-define=API_BASE_URL=https://<api-host>
flutter build apk --release
```

### Dashboard (Flutter Web)

```bash
cd dashboard
flutter create .
flutter pub get
flutter run -d chrome
flutter build web         # deploy build/web/ to any static host
```

## Pre-production checklist (Phase 12, not yet done)

- [ ] Replace `SECRET_KEY` / `ENCRYPTION_KEY` placeholders (never reuse `.env.example` values)
- [ ] CORS: restrict `allow_origins` in `backend/app/main.py` (currently `["*"]`)
- [ ] TLS 1.2+ enforced at the load balancer / reverse proxy
- [ ] Redis-backed rate limiting (100 req/min per IP)
- [ ] Enable + verify audit logging on all read paths (currently explicit per-endpoint)
- [ ] Data-retention / deletion jobs (Phase 11)
- [ ] Backup schedule (daily Postgres snapshots); quarterly encryption-key rotation
- [ ] CI gates: `pytest app/tests tests`, `test_phase2_services.py`, `flutter analyze`
- [ ] Security review: OWASP top-10, dependency scan, secrets manager, pen-test

## Operational notes

- **Health:** `GET /health` — status/service/version (for load balancers).
- **Auth:** 15-minute access tokens; clients should call `POST /api/v1/auth/refresh`
  (7-day refresh token) on 401. `POST /auth/logout` revokes the refresh token.
- **Offline sync:** mobile queues offline sessions/acks and replays them via
  `POST /api/v1/sync` (batch, idempotent); `GET /sync/pending/{patient_id}`
  reports queue depth.
- **Mock behavior:** without Bhashini/Anthropic keys the voice companion
  returns canned replies flagged `fallback: true` and RAG answers are
  extractive (no LLM). This is by design, not a misconfiguration.
- **Monitoring:** no Sentry/DataDog wired yet (Phase 12).

## Support

- Architecture decisions + compliance design: `CLAUDE.md`
- Phase tracker: `PHASE_1_STATUS.md`
- Run guide: `PHASE_1_QUICK_START.md` · Handoff: `PHASE_1_HANDOFF.md`
- Original plan (historic): `docs/superpowers/plans/2026-09-04-phase1-scaffold-data-models.md`
- Smart India Hackathon 2026 — SIH26003, MDoNER
