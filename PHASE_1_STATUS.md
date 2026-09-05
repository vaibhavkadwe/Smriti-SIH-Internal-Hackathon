# Phase Tracker — Elder-Care Cognitive Companion (SIH26003)

**Status:** Reconciled with the actual repository on 2026-09-04.
The original documents described Phase 1 as "ready to implement" and
DEPLOYMENT.md claimed "all 12 phases done"; both were out of date. This file
is the source of truth going forward.

All work is committed on `master` (commits `06c1bc2`, `d20c1c8`, `cb2f991`,
`18922a0`; root commit `a64aca7`).

## Completed

| # | Scope | Notes |
|---|---|---|
| 1 | Scaffold + data models + auth | 15 tables, JWT (15m/7d) + 5 roles, config, Docker, migration `0001` |
| 2 | Remaining models (SymptomLog, MedicalDocument, DocumentChunk) | Folded into all_models; RAG used from Phase 10 |
| 3 | Auth endpoints + consent flow | register/login/refresh/logout/me; patients CRUD + caregiver links; consent grant/list/revoke |
| 4–5 | Game engines | Match It (3 NER content packs, 27 multilingual items) + Routine Sequencing + rule-based adaptive difficulty |
| 6 | Reminder delivery + escalation | schedules/events/acknowledge; 10-min escalate + 3-missed-in-7d AlertFlag rules |
| 7 | Caregiver dashboard endpoints | rosters, 7-day summaries, alert acknowledgment |
| 8 | Real Bhashini integration | ULCA client, provider factory (`auto\|bhashini\|mock`), `/language/*`; activate with keys |
| 9 | Claude voice companion | shared `LLMClient`, DB-versioned system prompts + `/companion/config`, graceful fallback |
| 10 | RAG pipeline | overlap chunking, stable embeddings, threshold search, `/reports/documents/answer` |
| — | Flutter UIs wired | mobile (games/routine/reminders/companion/auth) + Flutter Web dashboard; **needs SDK to verify** |
| — | Offline-first layer | drift schema + replay sync outbox + local reminders; **needs `build_runner` codegen** |

## Remaining

| # | Scope | Notes |
|---|---|---|
| 11 | Compliance pass | retention/deletion jobs, endpoint-wide read-audit logging, consent-scope (purpose limitation) enforcement |
| 12 | Production hardening | CORS whitelist, real secrets/TLS, Redis rate limiting, CI gates, OWASP/pen-test, backups, data export |
| — | Live integration smoke tests | needs Bhashini + Anthropic keys (`BHASHINI_API_KEY`, `BHASHINI_USER_ID`, `ANTHROPIC_API_KEY`) |
| — | Mobile polish (v2) | real mic/TTS pipeline, gamified streaks, wearable + SMS fallback, ML alert rules |

## How the code is verified

```bash
# backend unit + API tests (SQLite in-memory, no DB needed)
cd backend && .venv/bin/python -m pytest app/tests tests -q     # 56 passed
.venv/bin/python test_phase2_services.py                        # 20 passed
```

To exercise the full stack you still need: Postgres + pgvector
(`docker compose up -d db` or your own), then `alembic upgrade head`
(the migration file exists; it has been validated via offline SQL rendering
but not yet applied to a live Postgres on this machine).

## Architecture references

- Decisions + compliance design: `CLAUDE.md`
- Run/deploy guide: `DEPLOYMENT.md`
- Original Phase 1 plan (historic, superseded by implementation):
  `docs/superpowers/plans/2026-09-04-phase1-scaffold-data-models.md`
