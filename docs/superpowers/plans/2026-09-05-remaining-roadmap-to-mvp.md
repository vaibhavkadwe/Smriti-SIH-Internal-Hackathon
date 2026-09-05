# Remaining Roadmap to a Production-Ready MVP — SIH26003

> Reconciled against the repository on 2026-09-05 (working tree clean at
> commit `4cc32ec`). Every item below is labeled
> **implemented / partially implemented / planned / not started**.
> Anything I cannot determine from the repo is flagged **NEEDS CONFIRMATION**.
>
> Companion files: `PHASE_1_STATUS.md` (phase tracker), `CLAUDE.md`
> (architecture), `DEPLOYMENT.md` / `PHASE_1_QUICK_START.md` (run guides),
> `backend/smoke_e2e.py` (live E2E — 45/45 green on Postgres 16).

---

## A. Current Status

### Where we are

**Phase boundary: end of Phase 10 (integration layers) — at the entrance to
Phase 11 (compliance pass).** The backend has been verified end-to-end against
a real Postgres 16 for the first time (migration `0001` applied cleanly; the
45-step smoke passes across patient/caregiver/clinician roles). No production
deployment exists and nothing has been exercised with real external services.

### Implemented + verified (do not rebuild)

| Area | State | Evidence |
|---|---|---|
| Data models — 15 tables, 17 PG enum types | ✅ implemented + verified | migration `0001` applies on live PG; enum `values_callable` fix (`4cc32ec`) |
| Auth (register/login/refresh/logout/me, JWT 15m/7d, 5 roles, bcrypt) | ✅ implemented + verified | E2E steps 1–11 |
| Patient profiles + caregiver links (+ no-implicit-access on `/patients`) | ✅ implemented + verified | E2E steps 12–14 |
| Games — Match It + Routine Sequencing, content packs (27×4 languages), adaptive difficulty | ✅ implemented + verified | E2E steps 15–23; commit fix for un-persisted sessions |
| Reminders — schedules/events/acknowledge/escalation-eval endpoints | ✅ implemented + verified | E2E steps 24–29 (manual eval only — see partial) |
| Dashboard — roster, 7-day summary, alert ack | ✅ implemented + verified | E2E steps 30–31 |
| Offline sync API — batch ingest + pending queue view | ✅ implemented + verified | E2E steps 32–33 (server stores outbox only — see partial) |
| Voice companion — DB-versioned prompts, config mgmt, chat (fallback mode) | ✅ implemented (mock) | E2E steps 34–38; real Claude needs key |
| Bhashini provider — ASR/TTS/NMT ULCA client + provider factory | ✅ implemented (mock) | E2E step 39; real API needs key |
| RAG — overlap chunking, stable embeddings, threshold retrieval, cited answers | ✅ implemented (JSON vectors, heuristic embeddings) | E2E steps 40–44 |
| DPDP — consent grant/list/revoke, audit helpers, Fernet encryption class | ✅ implemented (helpers) | E2E step 45; **enforcement not wired** |
| Flutter mobile + dashboard code wired to API | 🟡 code complete, **never compiled** | no Flutter SDK on dev machine |
| Offline-first mobile layer (drift outbox, replay sync, local notifications) | 🟡 code written, **no `.g.dart` codegen** | `mobile/lib/database/README.md` |
| Backend test suites | ✅ 57 pytest + 20 standalone green (SQLite) | run locally, no DB needed |

### Partially implemented (exists but incomplete — build on, don't rebuild)

1. **Reminder escalation is manual.** `POST /reminders/patients/{id}/evaluate-escalations`
   exists and is exercised, but CLAUDE.md Phase 6 specified an APScheduler job +
   notification fan-out to family/ASHA (10-min re-prompt, 3-missed-in-7-days
   → AlertFlag). No scheduler, no push/SMS/email delivery. *(Reminder events
   also aren't auto-generated from cadence server-side — the mobile schedules
   them locally.)*
2. **`/sync` is an outbox, not a pipeline.** `process_sync_batch` writes
   `sync_queue` rows and marks them `synced` immediately. Nothing consumes the
   queue to materialize domain rows (e.g. `offline_symptom` → `SymptomLog`,
   encrypted). Mobile replays *game sessions* through the live HTTP endpoints
   (correct), but queued reminder acks / symptom payloads need a consumer.
3. **DPDP enforcement exists as helpers only.** `ComplianceService.log_audit_access`,
   `verify_consent`, and `EncryptionService` are defined but not wired:
   - No audit on read paths (only explicit calls where code chose to).
   - `SymptomLog.notes` is stored plaintext despite the "Encrypted at rest"
     comment; `MedicalDocument.extracted_text` likewise.
   - No consent-scope (purpose-limitation) gate on data-access endpoints.
   - Access-control gaps verified in code: `GET /reminders/patients/{id}/events`,
     `GET /reminders/schedules/{id}`, and `GET /dashboard/patients/{id}/summary`
     accept **any authenticated user** with no ownership/link check; the
     companion chat allows any non-patient role without an active link.
4. **RAG uses heuristic embeddings stored as JSON**, not a vector type/model.
   Fine for a 45-step demo; not real retrieval.
5. **CORS is `*`; secrets are placeholders; no Redis usage at runtime; no rate
   limiting.**
6. **Flutter voice companion is text-only.** The mic/TTS pipeline is backend
   (Bhashini) + screen scaffolding, but no `speech_to_text` / audio plugins are
   wired on-device.

### Not started

- Phase 11 compliance pass (retention/deletion jobs, audit wiring, consent
  enforcement, access-control closure).
- Phase 12 hardening (CORS, rate limiting, real secrets, CI, security review).
- Live integration with real Bhashini / Claude keys.
- pgvector-native vector storage + a real embedding model.
- Flutter compile/verification, drift codegen, notification permission flow.
- Any deployment (no CI, no host, no secrets manager, no backups).

### Known gaps to watch (from the DB verification)

- Two auth import paths exist (`app.deps` and `app.middleware.auth_middleware`)
  but the middleware is a re-export shim — single implementation. OK, but
  consolidate to avoid drift.
- `backend/tests` and `backend/app/tests` split — keep both green; CI must run
  both plus `smoke_e2e.py` against Postgres.

---

## B. Remaining Phases

| Phase | Name | Summary | Depends on |
|---|---|---|---|
| 11 | DPDP compliance pass | retention/deletion jobs, endpoint-wide audit, consent-scope gates, access-control closure, column encryption, sync-queue consumer | nothing external |
| 12 | Production hardening | CORS whitelist, Redis rate limiting, real secrets/TLS, CI with PG service, backups | Phase 11 (cleanliness) |
| 13 | Real external services | live Bhashini (ASR/TTS/NMT) + Claude (companion + RAG answers) | API keys |
| 14 | RAG productionization | pgvector, real multilingual embedding model, retrieval/rerank tuning, real document corpus | DB decision, embedding provider, documents |
| 15 | Frontend verification & offline enablement | Flutter SDK build, drift codegen, notification permission flow, UI polish, sync-service call sites | Flutter SDK machine |
| 16 | Deployment & demo | host backend+DB, seed data, record demo, ops runbook | 11–15 |

Phases 11–12 and most of 16 are **input-independent** — they can be executed
now. 13–15 are partially blocked on **INPUTS** (Section H).

---

## C. Implementation Roadmap (ordered, dependency-aware)

### Step 1 — Phase 11: DPDP compliance pass (backend, no external inputs)

1. **Close access-control gaps** (reminders + dashboard): enforce
   patient-ownership / active caregiver-link on
   `GET /reminders/schedules/{id}`, `GET /reminders/patients/{id}/events`,
   `POST /reminders/events/{id}/acknowledge`, `GET /dashboard/patients/{id}/summary`,
   and companion chat for family_caregiver (reuse `_can_view_patient` from
   `patients.py` — promote it to a shared dependency).
2. **Wire audit logging**: add a dependency/service call to
   `log_audit_access(..., action="read")` on every health-data read
   (patient GET, events, summary, reports, RAG queries); keep write/delete
   audit at the service layer. Backfill `ip_address` from request.
3. **Consent-scope enforcement**: apply `verify_consent(patient_id, scope)`
   gates to scoped endpoints (symptom logs = `health_data`, companion =
   `voice_companion`, games = `game_data`). Decide behavior on missing consent
   (403 with clear message) — **NEEDS CONFIRMATION** on whether MVP requires
   hard-blocking or warn-only for the demo.
4. **Column-level encryption**: route `SymptomLog.notes` and
   `MedicalDocument.extracted_text` through `EncryptionService.encrypt` on
   write and `.decrypt` on read (service layer), respecting the existing
   comment contract in the models.
5. **Retention/deletion jobs**: an APScheduler (or simple
   asyncio-loop/`cron`) job implementing the retention table in CLAUDE.md
   (game 2y, symptom 1y, reminder 6mo, docs per-note-or-5y) plus the
   30-day-grace hard-delete after consent revocation (flag rows
   `revoked_at`, delete after grace).
6. **Sync-queue consumer**: drain `sync_queue` → materialize `offline_symptom`
   into encrypted `SymptomLog`; drop or explicitly ignore unsupported
   resource types with error rows (leave `retry_count`/`last_error` semantics).
7. **Verification**: extend `test_api_routes.py` (403 cases for cross-patient
   access; audit rows created per read; consent gate blocks scope-mismatch;
   encryption round-trips) and `smoke_e2e.py` steps.

### Step 2 — Phase 12: production hardening (backend + CI)

1. CORS whitelist via env (`CORS_ORIGINS`) in `main.py`.
2. Redis-backed rate limiting (slowapi or middleware; 100 req/min/IP);
   wire `REDIS_URL` for the first time.
3. Secrets: load `SECRET_KEY`/`ENCRYPTION_KEY` strictly from env; fail fast in
   production mode if placeholders; document rotation.
4. CI (GitHub Actions): run `pytest app/tests tests`, `test_phase2_services.py`,
   then boot Postgres service → `alembic upgrade head` → `smoke_e2e.py`.
5. OWASP-ish pass: dependency scan, `bandit`, input validation review.

### Step 3 — Phase 13: live external services (needs API keys)

1. Set `BHASHINI_API_KEY`/`BHASHINI_USER_ID` → switch provider off mock;
   verify ASR/TTS/NMT on a real NER-language audio sample.
2. Set `ANTHROPIC_API_KEY` → verify companion non-fallback replies + RAG
   answer synthesis with citations.
3. Add an integration test gate that skips when keys are absent.

### Step 4 — Phase 14: RAG productionization (needs decisions + data)

1. Switch `document_chunks.embedding` to `vector(N)` + pgvector HNSW index
   (new migration `0002`).
2. Adopt a real embedding model (see Section E) — provider choice is
   **NEEDS CONFIRMATION**.
3. Build the document-ingestion path from real artifacts (PDF/scan → text;
   OCR decision for scanned images).
4. Tune retrieval (top_k, min_similarity) + optional rerank; keep the
   Claude-grounded answer path with `[n]` citations + disclaimer.

### Step 5 — Phase 15: frontend verification & offline enablement (needs SDK machine)

1. `flutter create .` in `mobile/` and `dashboard/`; `pub get`;
   `dart run build_runner build` for drift.
2. `flutter analyze` clean; fix compile errors (first real compilation).
3. Wire the three documented sync hooks in `offline_sync_service` (start on
   app boot, enqueue on game-complete failure, enqueue on reminder-ack failure);
   implement the notification-permission flow.
4. Real mic/TTS on the companion screen (plugins) — or explicitly defer.

### Step 6 — Phase 16: deployment & demo

1. Provision host + managed Postgres (pgvector) (see Section H).
2. `alembic upgrade head` in prod; seed a demo patient/caregiver dataset with
   realistic NER content and documents.
3. Deploy dashboard/mobile artifacts; record the demo flow (login → play →
   dashboard alert → companion chat).

---

## D. Architecture (target)

```
Patient mobile app (Flutter)
 ├─ UI screens        ─┐
 ├─ drift SQLite outbox┼── offline-first: queue → replay via live API
 ├─ local notifications│
 └─ API client (JWT)  ─┘        │
                                 ▼
Caregiver dashboard (Flutter Web) ──► FastAPI backend (/api/v1, 50 routes)
                                       ├─ auth/RBAC (JWT 15m/7d, 5 roles)
                                       ├─ domain services (games, reminders,
                                       │   dashboard, patients, sync)
                                       ├─ compliance layer (consent scopes,
                                       │   audit, AES-256, retention jobs)
                                       ├─ speech: Bhashini (ASR/TTS/NMT)
                                       ├─ LLM: Claude (companion + RAG answers)
                                       └─ RAG: ingest → chunk → embed → pgvector
                                              retrieval → rerank(opt) → Claude
                                              response with citations
                                       │
PostgreSQL 16 + pgvector        Redis (rate limit, scheduler, cache)
   (single DB: relational + vector)
```

Integration points to verify in Step 1–5:
- Mobile `api_service.dart` ↔ every route already mirrored (verified by hand;
  must survive `flutter analyze`).
- `offline_sync_service` ↔ `POST /api/v1/sync` + live replay endpoints.
- `reminder_scheduler` ↔ local notification plugin (device permission flow).
- Backend ↔ Redis first use (rate limiting) and APScheduler (retention,
  escalation) — both currently unexercised dependencies.

---

## E. RAG Requirements

Pipeline status:

| Stage | Status | Gap |
|---|---|---|
| Document ingestion | 🟡 `POST /reports/documents/ingest` (text in) | real files: PDF parse, OCR for scans |
| Preprocessing / chunking | ✅ overlap chunking w/ word boundaries | tune per document type |
| Embeddings | 🟡 md5-weighted-TF heuristic vectors in JSON | **real model** — see below |
| Vector storage | 🟡 JSON column | pgvector `vector(N)` + HNSW (migration `0002`) |
| Retrieval | ✅ cosine + `min_similarity` threshold | index-backed query, rerank (optional) |
| Context construction | ✅ top-k chunks → citations | — |
| LLM response | ✅ Claude-grounded when key set; extractive fallback | live key |
| Answer safety | ✅ disclaimer, never diagnoses | keep |

**Recommendations (confirm before building):**
- **Embedding model:** `intfloat/multilingual-e5-small` (384 dims) run locally
  via sentence-transformers, or hosted `text-embedding-3-small` (1536) if a
  cloud key is acceptable. Multilingual coverage (Assamese/Bengali/Hindi) is
  the deciding factor — a pure-English model is **not** suitable.
  Claude has **no embeddings API** — do not plan on it. **NEEDS CONFIRMATION**
  on local-vs-hosted and preferred vendor.
- **Vector DB:** pgvector in the existing Postgres (already the architecture
  decision) — appropriate because it avoids a second datastore, supports
  HNSW, and the corpus (patient records) is small. 
- **Retrieval strategy:** cosine similarity via pgvector `<=>` with
  `min_similarity`; reranking optional for MVP (cross-encoder
  `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` if added).
- **LLM:** keep Claude (haiku for latency/cost, sonnet toggle for quality).
- **Documents needed from you:** sample prescriptions, clinician notes,
  cognition-assessment forms, diagnostic reports — one real corpus across the
  4 MVP languages, with PII stripped. See Section H.

---

## F. Database Requirements

- **Final DB:** PostgreSQL 16 + **pgvector** (unchanged architecture decision —
  confirmed appropriate; do **not** introduce a separate vector store).
  Redis stays as cache/queue/scheduler-broker only.
- **Current schema:** 15 tables (verified on live PG): `users`, `patients`,
  `caregiver_patient_links`, `consent_records`, `audit_logs`,
  `game_sessions`, `difficulty_adjustment_logs`, `reminder_schedules`,
  `reminder_events`, `alert_flags`, `sync_queue`, `symptom_logs`,
  `medical_documents`, `document_chunks`, `voice_companion_configs`.
- **Schema deltas required:**
  1. `document_chunks.embedding`: JSON → `vector(N)` (migration `0002`) +
     HNSW index (cosine). Also `patient_id` index on chunks.
  2. Retention-friendly index: `reminder_events(created_at)`,
     `symptom_logs(created_at)`, `game_sessions(completed_at)`,
     `sync_queue(synced_at)` (purging), `consent_records(revoked_at)`
     (grace deletion).
  3. Possibly `device_push_token`/notification fields on `users` or
     `patients` for reminder fan-out — **NEEDS CONFIRMATION** (FCM vs SMS vs
     local-only; see H).
- **Encryption at rest:** keep column-level AES-256 (Fernet) for
  `symptom_logs.notes`, `medical_documents.extracted_text`, `password_hash` —
  apply at the service layer (Step 1).

---

## G. API Requirements

### Already available (50 routes, verified)

Auth (5), patients (6), games (11), reminders (7), dashboard (3), sync (2),
language (4: status/asr/tts/translate), companion (5: chat text/voice +
config CRUD/activate), reports (4: ingest/query/answer/weekly-summary),
compliance (3: consent grant/list/revoke), health.

### Still required / deltas

| API | Why | Phase |
|---|---|---|
| `GET/POST /api/v1/compliance/audit-logs` (admin) | DEPLOYMENT.md promises it; read-audit visibility | 11 |
| `POST /api/v1/sync` consumer semantics (drain → domain rows) | outbox currently inert | 11 |
| Notification delivery endpoints / webhook or FCM token register | reminder fan-out per CLAUDE.md | 11/16 |
| Data export (per-patient JSON) — DPDP portability | listed Phase 12 backlog | 12 |
| `POST /api/v1/reports/documents/ingest` accepts real file uploads (multipart + OCR pipeline) | real artifacts | 14 |
| Admin: retention job status endpoint | ops visibility | 11 |
| **Validation/errors**: unify error envelope (detail) — largely consistent today; add 403 messages for consent/ownership gaps | consistency | 11–12 |
| **NEEDS CONFIRMATION**: do mobile auth flows require `/auth/refresh` rotation/token-revocation list, or is stateless logout acceptable for the demo? | security posture | 12 |

---

## H. INPUTS I NEED TO PROVIDE

| # | Input | Why / where used | Needed by phase |
|---|---|---|---|
| 1 | **Bhashini API key + user ID** | Live ASR/TTS/NMT; activates the provider currently in mock | 13 |
| 2 | **Anthropic API key** | Voice companion replies + RAG cited answers | 13 |
| 3 | **Embedding provider decision** (local sentence-transformers `multilingual-e5-small` vs hosted `text-embedding-3-small`) | fixes vector dimension + pgvector migration `0002` | 14 |
| 4 | **RAG document corpus** (stripped of PII): prescriptions, clinician notes, cognition assessments, ideally in Assamese/Bengali/Hindi/English | build + test the real retrieval pipeline | 14 |
| 5 | **Sample NER audio clips** for ASR/TTS testing (one per target language) | verify live Bhashini | 13 |
| 6 | **Flutter SDK environment** (a machine/CI where I can run `flutter create/pub get/build_runner/analyze`, or you run the listed commands and paste output) | mobile/dashboard have never compiled; drift codegen pending | 15 |
| 7 | **Deployment target decision** (Railway / Render / Fly / your VPS) + DB hosting (Neon / Supabase / RDS) | Phase 16; env + secrets layout | 16 |
| 8 | **Reminder notification channel decision** (local-only, FCM push, SMS provider like Twilio/MessageBird, or email) | determines whether fan-out needs a new integration | 11/16 |
| 9 | **Consent enforcement posture** for MVP (hard-403 vs warn) | Step 1.3 behavior | 11 |
| 10 | **Environment values**: real `SECRET_KEY`, `ENCRYPTION_KEY`, `CORS_ORIGINS`, `DATABASE_URL`, `REDIS_URL` for any non-local environment | Phase 12/16 | 12/16 |
| 11 | **Mobile device targets** (Android-only MVP? iOS too?) — affects plugins + testing | Phase 15 | 15 |
| 12 | **Timezone/reminder semantics**: are cadences local-device time or patient-region time? (affects `ReminderEvent` generation server-side) | 11/16 | 11 |

Anything not listed but named later in this doc is already determinable from
the repo and does not need your input.

### H.1 Mock-first dispositions (decided 2026-09-05 — implemented)

Development proceeds on every input using a clean interface + local mock
unless the input is genuinely required. Real integrations are later tasks.

| # | Input | Mock/local now | Real integration (later) | Status |
|---|---|---|---|---|
| 1 | Bhashini key | `LanguageServiceProvider` — `auto` falls back to Mock (ASR/TTS/NMT deterministic, no network) | set `BHASHINI_API_KEY`/`USER_ID`, flip provider | ✅ already mock |
| 2 | Anthropic key | `LLMClient` — canned companion reply / extractive RAG answer when key absent (`fallback:true`) | set `ANTHROPIC_API_KEY` | ✅ already mock |
| 3 | Embedding model | `EmbeddingProvider` interface; default `heuristic` (deterministic md5-TF, no deps); `local`/`openai` adapters built but unavailable backends degrade to heuristic with warning | install sentence-transformers (e5) or add OPENAI_API_KEY; pgvector migration | ✅ interface + heuristic shipped |
| 4 | RAG document corpus | `backend/seed_demo.py` — clearly-labeled `[SYNTHETIC DEMO]` bilingual (EN/AS/BN/HI) documents | PII-stripped real records | ✅ synthetic corpus shipped |
| 5 | NER audio clips | Mock ASR ignores audio bytes → canned transcript; voice pipeline mock-tested | real clips per language | ✅ covered by mock |
| 6 | Flutter SDK | **genuinely required** for compile/codegen — nothing else unblocks Phase 15 | install on this machine (`brew install --cask flutter`) or run commands on an SDK box | ⬜ blocking Phase 15 only |
| 7 | Deployment target | docker compose + runbook exist; local PG cluster repeatable | provision host + managed PG | ⬜ Phase 16 |
| 8 | Notification channel | `NotificationProvider` ABC + `console` transport (logs + in-memory `deliveries`); escalation fan-out wired to family/ASHA via `notify_escalation_results` | implement `sms`/`fcm`/`email` adapters behind the same ABC | ✅ console transport shipped |
| 9 | Consent posture | default `strict` (403) is DPDP-correct; warn mode later via settings flag if demo needs it | — | ✅ decided (strict) |
| 10 | Real secrets | env-driven already; `.env.example` documents each | secrets manager at deploy | ✅ non-blocking |
| 11 | Device targets | Android-first assumed (README) | confirm iOS | ✅ decided |
| 12 | Timezone semantics | decision: mobile fires local notifications by device time; server stores UTC instants; cadence strings parsed per event | patient-region timezone field (v2) | ✅ decided |

New backend surface shipped with this pass (all tested, 80 pytest + 20
standalone): `embedding_provider.py`, `notification_service.py`,
`retention_service.py`, sync outbox→consumer (`offline_symptom` → encrypted
`SymptomLog`), escalation fan-out hook, `seed_demo.py`. Verified live on
Postgres 16 (migration → seed → consume → escalate → RAG query).

---

## I. Testing Checklist

| Layer | How | Command / gate |
|---|---|---|
| Backend unit + API (SQLite) | pytest | `pytest app/tests tests -q` — 57 green |
| Backend standalone services | script | `python test_phase2_services.py` — 20 green |
| Live E2E (real Postgres) | smoke | `alembic upgrade head` then `python smoke_e2e.py` — 45 green |
| DB migration on clean DB | alembic | part of CI job (Postgres service) |
| Enum regression guard | metadata test | `test_all_enum_columns_persist_lowercase_values` |
| Phase 11 (new tests) | pytest | 403 cross-access; audit row per read; consent scope blocks; encryption round-trip; retention job removes rows |
| Phase 13 (gated on keys) | pytest | companion non-fallback reply; real ASR/TTS round-trip; RAG answer with citations |
| Phase 14 | pytest | ingestion of real files; pgvector query returns indexed results above threshold |
| Phase 15 | flutter | `flutter analyze` clean; widget test on login→home; drift codegen compiles |
| Edge cases to cover | | duplicate caregiver link (409 exists), revoked-token reuse, empty routines (sequencing board), consent revocation mid-session, offline→online replay ordering, 401→refresh retry, oversized audio/doc payloads |

---

## J. Final MVP Checklist (definition of done)

- [ ] Backend: Phases 1–12 implemented; **57+ pytest, 20 standalone, 45 E2E green** in CI against Postgres.
- [ ] Compliance: audit on every health-data read; consent gates active; sensitive columns encrypted; retention + grace-deletion jobs running; access-control gaps closed.
- [ ] Live services: Bhashini ASR/TTS/NMT + Claude companion + RAG answers verified with real keys (integration tests gated on key presence).
- [ ] RAG: real embedding model, pgvector storage with HNSW, cited answers, disclaimer.
- [ ] Mobile (Android at minimum): compiles (`flutter analyze` clean), drift codegen done, offline sync hooks live, local notifications fire, companion does real audio or an explicit documented deferral.
- [ ] Dashboard (web): compiles, roster → summary → alerts flow works against deployed backend.
- [ ] Deployment: backend + PG(pgvector) hosted, CORS whitelisted, real secrets in a secrets manager, rate limiting on, TLS enforced, backups scheduled.
- [ ] Demo script recorded: elder registers/plays offline → syncs → caregiver sees trends + alert → acks → companion chat answers.
- [ ] Security review pass (OWASP top 10 + DPDP privacy review) signed off.

---

## Suggested execution order (what to do when)

1. **Now (no inputs needed):** Phase 11 backend compliance pass → Phase 12 backend hardening → CI wiring.
2. **In parallel, gather inputs** #1–#5 (keys, decisions, docs, audio).
3. **When keys arrive:** Phase 13 live verification.
4. **When embedding decision + docs arrive:** Phase 14 RAG productionization.
5. **On an SDK machine:** Phase 15 frontend compile + offline enablement.
6. **When target chosen:** Phase 16 deployment + demo.
