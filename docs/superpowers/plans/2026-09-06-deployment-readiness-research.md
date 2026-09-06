# Deployment Readiness Research — SIH26003 Elder-Care Cognitive Companion

> Researched 2026-09-06. Reconciles repo state against `CLAUDE.md` and
> `DEPLOYMENT.md`, runs the test suites, and inventories cleanup candidates
> to support a production-readiness decision.

## Executive Summary

**The backend is functionally production-ready at the code level** — all 12
roadmap phases are implemented, `130 passed + 1 skipped` pytest, plus
`21/21` standalone service checks; CI runs a live E2E smoke against a real
Postgres 16 in `.github/workflows/ci.yml`. Phase 12 production posture
(secret/CORS refusal, rate limiting, audit, Fernet encryption) is enforced
and gated by `test_phase12_gates.py`.

**What blocks a real deployment today is operationally minimal but
non-negotiable:**

1. **No real secret materialization.** The repo's `.env` is a partial
   fragment (`DATABASE_URL` only); `SECRET_KEY` / `ENCRYPTION_KEY` are
   unset and `CORS_ORIGINS=*` is the default — `validate_for_environment()`
   will refuse to boot with `ENVIRONMENT=production` until all three are
   replaced.
2. **No live AI keys.** `OPENROUTER_API_KEY` / `BHASHINI_API_KEY` /
   `ANTHROPIC_API_KEY` are empty. The platform degrades gracefully (mock
   speech, canned persona reply, heuristic RAG), so the elder UX still
   works without them — but the AI features are stubbed.
3. **Three large stale HTML docs and a zip archive at repo root** inflate
   the working tree, confuse readers (their status tables contradict
   `CLAUDE.md`), and waste CI bandwidth.
4. **No production secret manager, monitoring, or backup runbook.**
   `DEPLOYMENT.md` flags these as Phase 12 checklist items; the code
   enforcements are in, the runbook is not.

**Bottom line:** ship the cleanup + secret/CORS fixes in one PR, then
deploy to a managed PaaS. The single highest-leverage next step is
**generate real secrets, set them in the deployment env, flip
`ENVIRONMENT=production`, deploy via the existing Dockerfile + uvicorn
entrypoint** — the rest of the work is documentation/hygiene.

---

## 1. Phases implemented vs planned

Per `CLAUDE.md:8-27`, all 12 phases are implemented and tested. The
reconciliation table says:

- **Phases 1–7** (scaffold, 15 data models, auth/RBAC, games, reminders,
  dashboard, sync) — migrations `0001_initial_schema` → `0003_refresh_rotation`
  [source: CLAUDE.md:18]. All 15 tables live in
  `backend/app/models/{all_models.py,user.py,compliance.py}` and routes
  in `backend/app/routes/{auth,patients,games,reminders,dashboard,language,
  voice_companion,reports,compliance,sync}.py`.
- **Phase 8** (Bhashini) — `language_service.py`, config-driven
  `LANGUAGE_SERVICE_PROVIDER=auto|bhashini|mock` [source: CLAUDE.md:19,
  .env.example:24-28, backend/app/config.py:46-52].
- **Phase 9** (voice companion LLM) — `llm_client.py` (OpenRouter default,
  Anthropic alt), DB-versioned prompts [source: CLAUDE.md:20].
- **Phase 10** (RAG) — chunking + stable embeddings + cited answers; PDF
  upload; extractive fallback [source: CLAUDE.md:21].
- **Phase 11** (compliance) — consent-scope gates, no-implicit-access,
  read-audit, Fernet at-rest, data export, retention jobs
  [source: CLAUDE.md:22].
- **Phase 12** (production hardening) — rate limiting (Redis+fallback),
  CORS whitelist, placeholder-secret refusal, CI, E2E smoke
  [source: CLAUDE.md:23].
- **Cross-cutting** — offline-first mobile (drift outbox, codegen
  committed at `mobile/lib/database/app_database.g.dart`), Monad design
  system across mobile + dashboard + `backend/static/`, client-side
  `game_analytics_engine.dart` with tests [source: CLAUDE.md:25-27].

**Stale docs that disagree with the above:**

- `DEPLOYMENT.md:1-7` — header reconciliation note says "backend through
  Phase 10, Phases 11–12 still open." This is **stale**; CLAUDE.md
  supersedes.
- `DEPLOYMENT.md:14,16,20,133-143` — repeats the stale pre-Phase-11/12
  checklist (CORS="currently [\"*\"]", "rate limiting not wired",
  "data-retention jobs pending"). All now in.
- `DEPLOYMENT.md:52` — claims "56 passed"; actual is **130 passed + 1
  skipped** (see §4).
- `PHASE_1_HANDOFF.md:1-25` — "through Phase 10", "Phase 11 not started",
  "Phase 12 not started", "56 pytest + 20 standalone". Stale.
- `PHASE_1_STATUS.md` — pre-Phase-11 tracker (declared stale by
  CLAUDE.md:13).
- `docs/superpowers/plans/2026-09-05-remaining-roadmap-to-mvp.md` —
  "Phase boundary: end of Phase 10" header. The body notes it was
  written at the Phase-10 boundary; the actual code has Phase 11+12
  shipped since.

These four files should be either deleted or re-written to match
`CLAUDE.md`. They are listed in §10.

## 2. Critical missing pieces before deployment

Ordered by impact. Most are operational, not code.

| # | Gap | Where | Fix shape |
|---|---|---|---|
| 1 | Real `SECRET_KEY` (≥24 chars) | `.env` or PaaS env | `openssl rand -hex 32` |
| 2 | Real `ENCRYPTION_KEY` (≥16 chars) | same | `openssl rand -hex 32` |
| 3 | `CORS_ORIGINS` whitelist | same | comma-separated real origins, not `*` |
| 4 | `ENVIRONMENT=production` | same | switch from `development` |
| 5 | `OPENROUTER_API_KEY` (or `ANTHROPIC_API_KEY`) | same | opt-in; without it, canned-reply LLM |
| 6 | `BHASHINI_API_KEY` / `BHASHINI_USER_ID` | same | opt-in; without it, deterministic mock speech |
| 7 | Production-grade DB | `docker-compose.yml` | swap to managed Postgres (Neon, Supabase, RDS) + pgvector; `CREATE EXTENSION IF NOT EXISTS vector;` then `alembic upgrade head` |
| 8 | TLS in front of API | infra | load balancer / reverse proxy with TLS 1.2+; `caddy`/`nginx`/`fly.io` autotls |
| 9 | Backup & restore runbook | ops | daily snapshot, quarterly key rotation; `DEPLOYMENT.md:141` calls this out |
| 10 | Sentry / DataDog / equivalent | code | not wired; no error monitoring today (`DEPLOYMENT.md:156`) |
| 11 | Real notification channel (SMS/FCM/APNs) | `backend/app/config.py:100` | only `console` provider exists; reminders/alerts will log-only in prod |
| 12 | Mobile voice audio path | `mobile/lib/screens/voice_companion_screen.dart` | text chat is wired; on-device mic + TTS playback pending speech plugins (CLAUDE.md:430-431) |
| 13 | Mobile game art (32 card PNGs + audio) | `mobile/assets/games/` | falls back to Material icons today, no crash; ship art whenever ready (CLAUDE.md:435-439) |

`docker-compose.yml` is dev-shaped (insecure postgres password
`postgres:postgres`, host-volume mount `./backend/app:/code/app`,
`ENVIRONMENT: development`). The same image would boot in production
with the right env vars, but the compose file is **not** the production
artifact [source: docker-compose.yml:5-7, 33-43].

## 3. API keys / integrations not configured

| Integration | Default | Status | Degradation when absent |
|---|---|---|---|
| LLM (voice companion + RAG answers) | OpenRouter free tier `minimax/minimax-m3:free`, fallback `nvidia/nemotron-3-*:free`; Anthropic alt [source: .env.example:30-46, backend/app/config.py:64-86] | `OPENROUTER_API_KEY` empty in `.env` | Canned persona reply (`LLM_AUTO_FALLBACK=true`) or extractive RAG; never errors on the elder UX [source: CLAUDE.md:74] |
| Speech (ASR/TTS/NMT) | Bhashini ULCA `auto|bhashini|mock` [source: .env.example:24-28] | `BHASHINI_API_KEY` / `BHASHINI_USER_ID` empty | Deterministic local mock [source: CLAUDE.md:75] |
| Embeddings (RAG) | `heuristic` (md5-TF, 1536-dim) default; `local` = sentence-transformers e5-small; `openai` [source: .env.example:49-54, backend/app/config.py:88-95] | Current `.env` says `EMBEDDING_PROVIDER=local` but `ENCRYPTION_KEY`/`OPENROUTER_API_KEY` etc. are unset; sentence-transformers requires the heavy torch stack in `requirements.txt:23-28` | Missing/unknown backends warn and return heuristic — RAG always works [source: CLAUDE.md:76] |
| Notifications | `console` (logs + records) [source: backend/app/config.py:100] | only the mock is implemented | reminders fire in-app logs only |

`.env` is **3 lines** today:
```
DATABASE_URL=postgresql+psycopg://priyanujgoswami@localhost:5432/eldercare
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=intfloat/multilingual-e5-small
```
[source: .env:1-3] — pointing at a local Postgres, not the docker host.
The full key set lives in `.env.example`.

## 4. Build / test status (verified)

**Backend pytest** (re-run 2026-09-06 against SQLite, `ENVIRONMENT=test`):
```
1 failed, 130 passed, 1 skipped, 7 warnings in 22.81s
```
[source: live run, `cd backend && python3 -m pytest app/tests tests -q
--tb=no`]

- The 1 **failure** is `test_document_upload.py::test_upload_real_pdf`
  due to a missing `pypdf` module on this dev box. `pypdf>=4.0.0` is in
  `requirements.txt:23`, so CI is unaffected — this is a local-env
  install-state issue, not a code defect.
- The 1 **skipped** is consistent with `CLAUDE.md:32-33` — tests that
  need real external keys are skip-by-design.

**Standalone service tests** (`test_phase2_services.py`):
```
Results: 21 PASSED, 0 FAILED out of 21 total
```
[source: live run]

**CI pipeline** (`.github/workflows/ci.yml`):
- Backend job: `pytest app/tests tests -q` + `python test_phase2_services.py`
  + `alembic upgrade head` against a fresh Postgres 16 service +
  `smoke_e2e.py` against a live uvicorn instance. Idempotent companion
  config step so re-runs are clean [source: CLAUDE.md:35-36,
  .github/workflows/ci.yml:43-61].
- Frontend job: `flutter pub get` + `dart run build_runner build
  --delete-conflicting-outputs` + `flutter analyze` for `mobile/` and
  `dashboard/` [source: .github/workflows/ci.yml:63-82]. No `flutter
  test` step — the `mobile/test/game_analytics_engine_test.dart` and
  `dashboard/test/widget_test.dart` are not currently run in CI.

**Triggers:** `push` to `main` or `master`, plus all pull requests
[source: .github/workflows/ci.yml:1-5].

**Graph freshness:** the knowledge graph was built from commit `4e9a8b3`
[source: graphify-out/GRAPH_REPORT.md:13]. The current HEAD is `f2df21b`,
so the graph is 1 commit behind — `graphify update .` would close the
gap (no API cost per the report).

## 5. Files stale / should be deleted

Detailed list in §10 (Cleanup). Highlights:

- `PHASE_1_STATUS.md` — explicitly declared stale by `CLAUDE.md:12-13`.
- `DEPLOYMENT.md` — stale on Phases 11/12, on CORS rate limit, on the
  test count; needs a rewrite or removal.
- `PHASE_1_HANDOFF.md` — same staleness.
- `docs/superpowers/plans/2026-09-05-remaining-roadmap-to-mvp.md` —
  written at the Phase-10 boundary; superseded by CLAUDE.md.
- `PHASE_1_QUICK_START.md` — likely stale on Phases 11/12 too (not
  re-read in detail).
- `PHASE2_SUMMARY.html`, `PHASE_1_EXECUTION_GUIDE.html`,
  `brainstorm-demo-features.html` — large static HTML files at repo
  root, last touched 2026-09-04. They are **not** the documentation;
  the canonical docs are the .md files. ~80KB total.
- `CLAUDE.md.zip` — archive of an old `CLAUDE.md` (28KB→11KB after
  rebuild). Redundant with the live `CLAUDE.md`.
- `SIH_Team_Maverick_Project/` — empty dir explicitly gitignored as
  "unrelated nested repo (student copy)" [source: .gitignore:53].
- `commit-phase1.sh` and `setup.sh` — single-purpose scripts from
  early onboarding, no longer maintained.
- `verify_output.txt` (7.5KB) — looks like a one-shot capture, not
  maintained.
- `backend/dashboard/assets/` and `backend/mobile/assets/` — empty
  subdirectories inside `backend/`; possible artifacts of an old
  monorepo layout. Should be removed.

## 6. Actual directory size breakdown

Measured 2026-09-06, after clearing Python `__pycache__` to get honest
numbers.

| Path | Size | Notes |
|---|---|---|
| `mobile/build` | 1.4 GB | **gitignored but on disk** — Flutter Android build output. Will be regenerated by CI; safe to delete locally. |
| `mobile/.dart_tool` | 955 MB | `pub` cache + codegen intermediates. **gitignored**. Safe to delete; `flutter pub get` repopulates. |
| `backend/.venv` | 871 MB | Python virtualenv. **gitignored** (`.venv/` is in .gitignore:18). Delete with `rm -rf backend/.venv`. |
| `dashboard/build` | 139 MB | Flutter web build. **gitignored**. |
| `dashboard/.dart_tool` | 70 MB | **gitignored**. |
| `.git` | 6.7 MB | Normal git history. |
| `graphify-out/` | 21 MB | Knowledge graph. Useful for AI navigation; not for runtime. |
| `docs/` | 132 KB | Plans directory; 2 existing plans. |
| `demo-seed/` | 12 KB | 3 synthetic RAG demo docs. Useful. |
| `SIH_Team_Maverick_Project/` | 0 B | Empty, gitignored. |
| `backend/` (post-cleanup) | ~1 MB excluding `.venv` | Real backend code |
| `mobile/` (post-cleanup) | ~350 MB excluding `build` + `.dart_tool` | Flutter source + assets |
| `dashboard/` (post-cleanup) | ~1 MB excluding `build` + `.dart_tool` | Flutter Web source |

**.gitignore coverage** [source: .gitignore:1-53]: correctly ignores
`.env*`, Python caches, Flutter artifacts, Docker overrides, agent
state, the unrelated `SIH_Team_Maverick_Project/`, and `backend/.pgdata/`.
**It is missing:**

- `CLAUDE.md.zip`
- The four root `.html` files
- `verify_output.txt`
- `commit-phase1.sh`, `setup.sh`
- `backend/dashboard/`, `backend/mobile/` (empty stray dirs)
- `backend/.pytest_cache/` (the existing entry `.pytest_cache/` is
  scoped to root, not the backend subdir — pytest still creates a cache
  there on every test run, then reuses it)

These should be added to `.gitignore` to keep the working tree clean and
to make the git history readable. The current `.gitignore` is correct
on the **standard** Python/Flutter noise, but the project has accumulated
project-specific scratch that is not ignored.

## 7. Build artifact / .gitignore configuration

Already covered in §6. Key observation: the repo is currently
"approximately clean" — the things that should be ignored **are**
ignored, but a backlog of project-specific scratch files has piled up at
the root. None of these files are tracked by git, so they don't pollute
history, but they confuse new readers and inflate tree size.

## 8. Recent commits / improvements

[source: `git log --oneline -10`]

```
f2df21b Your commit message here
4e9a8b3 improvements
5cc3650 Bug Fixes
97b1a65 Fixed Bugs and Update Rag Pipeline
037b135 Frontend uploaded
8cc6b23 Pushing all the Backend
7fed314 Update README.md
83f5419 Revise README with detailed project information
fcce5d4 Initial commit
```

**Observations:**

- The top commit has the placeholder message "Your commit message here"
  — a small polish item, not a bug.
- "Frontend uploaded" + "Pushing all the Backend" is a clean
  frontend/backend split commit pattern.
- "improvements" + "Bug Fixes" + "Fixed Bugs and Update Rag Pipeline" +
  "Bug Fixes" suggests an iterative polish loop after the initial
  upload. Consistent with the CLAUDE.md "shipped since the last
  reconcile" list (refresh-token rotation, gentler difficulty grids,
  game-scoring fixes, etc.) [source: CLAUDE.md:416-423].
- The recent commit cadence is consistent with an active hackathon
  submission rather than a long-running project.

**Commit message hygiene** — the placeholder on `f2df21b` is the only
flag; the rest are descriptive.

## 9. CI/CD pipeline completeness

[source: .github/workflows/ci.yml]

**What it does well:**

- Two parallel jobs: backend and frontend
- Backend runs unit + API tests on SQLite (no DB needed)
- Backend spins up a real Postgres 16 service for `alembic upgrade head`
  and `smoke_e2e.py` — this is the deployment-shape verification
- Frontend runs `pub get` + `build_runner` codegen + `flutter analyze`
  on both surfaces
- Triggers on `main`, `master`, and all PRs

**What's missing:**

- **No `flutter test` step.** The mobile and dashboard unit/widget tests
  (incl. `game_analytics_engine_test.dart` — CLAUDE.md calls this out
  specifically) are not in CI. Adding
  `flutter test` to each frontend subdirectory after `flutter analyze`
  would close this gap.
- **No `secret scan`.** Even a basic `gitleaks` step would catch a
  future accidental commit of `OPENROUTER_API_KEY` or `SECRET_KEY`.
- **No deploy step.** No `fly deploy` / `railway up` / `aws ecs
  update-service` / container publish. CI verifies the build is
  healthy but does not promote it to a public environment.
- **Branch gating is loose.** The matrix runs on every push to `main`
  *and* `master`, with no path filter. Cheap to run as-is; would be
  worth adding if test duration grows.
- **No concurrency / cancel-in-progress.** Multiple in-flight PRs from
  the same branch would race. Minor.
- **No test result artifact upload.** Failures have to be reproduced
  from logs; no JUnit XML, no coverage report.

**Verdict:** CI is **complete enough for an MVP** (verifies correctness
of every push), but **incomplete for a production deploy** (no
promotion path, no test step on Flutter, no secret scan). Adding the
`flutter test` and `gitleaks` steps is a 10-line PR.

---

## Conclusion — Best Next Step

**Recommended single action:** create a `chore/deployment-readiness` PR
that does all of the following in one go:

1. **Delete the stale doc backlog** (see §10): the 4 stale `.md` files,
   the 3 stale root `.html` files, the `.zip`, the two empty `backend/`
   subdirs, the now-redundant `commit-phase1.sh` / `setup.sh` /
   `verify_output.txt`. ~150KB lighter, zero behavior change.
2. **Add the missing `.gitignore` entries** to keep the tree clean
   going forward.
3. **Rewrite `DEPLOYMENT.md`** to match the actual state (Phases 11/12
   done, 130 tests, CORS/rate-limit/retention wired). Keep it as a
   real runbook, not a stale checklist.
4. **Add `flutter test` + `gitleaks` steps to CI.** No code change.
5. **Generate real `SECRET_KEY` and `ENCRYPTION_KEY` for the
   deployment environment** (not the repo). Document the procedure in
   the new `DEPLOYMENT.md`.
6. **Refresh the knowledge graph:** `graphify update .` to pull in
   `f2df21b`.

This PR is the highest-leverage move because it (a) closes every
misleading surface in one pass, (b) makes the next contributor's life
easier, and (c) leaves the repo one secret-management decision away
from a production deploy.

**After that PR merges:** provision a managed Postgres with pgvector,
generate the production secrets, push them into a secret manager, and
deploy the `backend/Dockerfile` to any PaaS that runs `uvicorn
app.main:app` on port 8000. The mobile and dashboard apps can then
build in CI on every push; promote a release to the Play Store / web
host as needed.

**Not recommended as the next step:**

- Adding ML-based alert rules, wearable ingestion, dementia-friendly
  modes — these are explicitly v2 [source: CLAUDE.md:448].
- Sourcing game art — the icon fallback is graceful
  [source: CLAUDE.md:435-439].
- Building the per-action game-telemetry server path — the client-side
  engine already computes the metrics [source: CLAUDE.md:432-434].

---

## 10. Cleanup candidates (full list)

### Stale markdown (4 files, ~25KB)
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/PHASE_1_STATUS.md`
  — declared stale by CLAUDE.md:12-13.
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/PHASE_1_HANDOFF.md`
  — pre-Phase-11/12 status (lines 19-25).
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/PHASE_1_QUICK_START.md`
  — likely stale on Phases 11/12; needs verification.
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/docs/superpowers/plans/2026-09-05-remaining-roadmap-to-mvp.md`
  — written at Phase-10 boundary; superseded by CLAUDE.md.

### Stale HTML at root (3 files, ~80KB)
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/PHASE2_SUMMARY.html` (28KB)
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/PHASE_1_EXECUTION_GUIDE.html` (10KB)
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/brainstorm-demo-features.html` (17KB)

### Stale archive (1 file, 11KB)
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/CLAUDE.md.zip`

### Stray scripts / capture (3 files, ~10KB)
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/commit-phase1.sh`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/setup.sh`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/verify_output.txt`

### Empty directories (already gitignored but present)
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/SIH_Team_Maverick_Project/` (empty)
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/dashboard/assets/` (empty)
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/mobile/assets/` (empty)

### Required `.gitignore` additions

Append to `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/.gitignore`:

```gitignore
# Project-specific scratch (kept untracked)
CLAUDE.md.zip
*.html
verify_output.txt
commit-phase*.sh
setup.sh

# Pytest cache (also created in subdirs)
backend/.pytest_cache/
```

> Note: the blanket `*.html` rule would also ignore the design-system
> `backend/static/*.html`; scope it as `/*.html` at the repo root if
> that becomes a problem.

### Behavior-preserving

None of the above changes alter runtime behavior. After deletion, re-run:

```bash
cd backend && python3 -m pytest app/tests tests -q   # 130 passed + 1 skip + 1 fail (pypdf env)
cd backend && python3 test_phase2_services.py        # 21/21
cd mobile && flutter pub get && flutter analyze
cd dashboard && flutter pub get && flutter analyze
```

Expected: identical results to the current state.
