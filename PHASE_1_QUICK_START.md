# Quick Start — Elder-Care Cognitive Companion (SIH26003)

> Reconciled with the repository on 2026-09-04. This file is the practical
> "run it now" guide. For the phase-by-phase accounting see
> `PHASE_1_STATUS.md`; for production deployment see `DEPLOYMENT.md`.

## Repo at a glance

```
backend/          FastAPI app — models, routes, services, Alembic migration 0001
mobile/           Flutter patient app (games, reminders, companion, offline layer)
dashboard/        Flutter Web caregiver dashboard
docker-compose.yml  Postgres(pgvector) + Redis for local dev
.env.example      All environment variables, documented
CLAUDE.md         Architecture decisions + compliance design
PHASE_1_STATUS.md Phase tracker (source of truth)
```

## Backend — run it

```bash
# 1. (Optional) Postgres + Redis — or point DATABASE_URL at your own PG
docker compose up -d

# 2. Install + configure
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env      # fill in secrets; defaults work for local dev

# 3. Create schema (migration 0001 — all 15 tables)
alembic upgrade head

# 4. Start the API
uvicorn app.main:app --reload   # Swagger UI at http://localhost:8000/docs
```

Verify it is up:

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"Elder-Care Cognitive Companion","version":"0.1.0"}
```

The API exposes **50 routes** (49 under `/api/v1` + `/health`): auth,
patients, games, reminders, dashboard, language (Bhashini), voice companion,
reports (RAG), compliance, and the offline `/sync` endpoint. Full list in the
Swagger UI.

## Backend — test it (no database required)

```bash
cd backend
.venv/bin/python -m pytest app/tests tests -q   # 56 tests — unit + API level
.venv/bin/python test_phase2_services.py        # 20 standalone service checks
```

Both suites run against an in-memory SQLite database, so they work without
Postgres or Redis. The only thing not exercised locally is the Alembic
migration against a real Postgres (validated via offline SQL rendering —
apply with `alembic upgrade head` once a DB is up).

## Enabling the real AI services (Phases 8–10)

Out of the box the backend runs in **mock/fallback mode** — no keys needed.
To go live, put real credentials in `.env` (zero code changes):

| Service | Env vars | Effect when set |
|---|---|---|
| Bhashini ASR/TTS/NMT | `BHASHINI_API_KEY`, `BHASHINI_USER_ID` | `LANGUAGE_SERVICE_PROVIDER=auto` stops falling back to Mock |
| Claude companion + RAG answers | `ANTHROPIC_API_KEY` | Companion chat + `/reports/documents/answer` use real Claude |

## Flutter apps (need the Flutter SDK)

The Dart code is written and wired to the API, but this machine has no
Flutter SDK, so nothing has been compiled yet. On a machine with the SDK:

```bash
# Patient app
cd mobile
flutter create .     # generate platform folders (never created)
flutter pub get
dart run build_runner build --delete-conflicting-outputs   # drift .g.dart codegen
flutter run          # point at your backend:
                     #   --dart-define=API_BASE_URL=http://<host>:8000

# Caregiver dashboard (Flutter Web)
cd ../dashboard
flutter create .
flutter pub get
flutter run -d chrome
```

More on the offline layer (drift schema, replay sync, local notifications):
`mobile/lib/database/README.md`.

## Typical end-to-end flow (once everything runs)

1. `POST /api/v1/auth/register` as a `patient` (auto-creates a `PatientProfile`).
2. `POST /api/v1/auth/login` → access (15 min) + refresh (7 days) tokens;
   `POST /auth/refresh` and `POST /auth/logout` exist too.
3. `GET /api/v1/games/content-packs` → pick a pack →
   `GET /content-packs/{pack_id}/board` → play → `POST /games/sessions/{id}/actions`
   and `/complete` (server computes accuracy + response-time metrics).
4. `GET /api/v1/reminders/schedules/{patient_id}` → acknowledge events with
   `POST /reminders/events/{event_id}/acknowledge`.
5. Caregiver/ASHA/clinician login → `GET /api/v1/dashboard/caregivers/{id}/patients`
   → patient summaries → acknowledge alert flags.
6. Offline: the mobile app queues sessions/acks and replays them through
   `POST /api/v1/sync` on reconnect.

## Troubleshooting

- **`alembic upgrade head` fails / no database** — start `docker compose up -d`
  or set `DATABASE_URL` to a reachable Postgres 15+ with pgvector.
- **Auth 401s** — tokens are short-lived (15 min); use `/auth/refresh`.
- **Voice/companion returns canned text** — no `ANTHROPIC_API_KEY` set;
  that is the designed fallback (`LLM_AUTO_FALLBACK=true`).
- **Everything else** — see `docs/superpowers/plans/2026-09-04-phase1-scaffold-data-models.md`
  for the original implementation plan, and `CLAUDE.md` for architecture decisions.
