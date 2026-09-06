---
milestone: caregiver-dashboard-milestone
verified: 2026-09-06T15:30:00Z
status: passed
related: mobile caregiver dashboard rebuild + api_service extensions (same endpoints as web dashboard)

## Integration Verification Report

**Milestone:** Native caregiver dashboard (mobile) — roster, summary, trends, compliance log, risk flags, schedule editing, DPDP audit

### Integration Points Tested

| Integration Point | Status | Details |
|-----------------|--------|---------|
| Auth login/refresh | ✓ | JWT + refresh flow working; 401 on missing/garbage token |
| Patient roster | ✓ | `GET /dashboard/caregivers/{id}/patients` — 200, correct shape |
| Patient summary | ✓ | `GET /dashboard/patients/{id}/summary` — 200; tier-gated fields stripped server-side (view=basic) |
| Reminder events | ✓ | `GET /reminders/patients/{id}/events` — 200, real event IDs + status incl. escalated |
| Schedules create/list/delete | ✓ | Full lifecycle persisted and re-read (create→list shows→delete→gone) |
| Alert acknowledge | ✓ | 200 on valid; 404 on nonexistent (clean error contract) |
| Audit logs (DPDP) | ✓ | 403 for family role — UI shows honest "admin-only" note; gate is server-side |
| Game telemetry → summary | ✓ | Patient session+action+complete → caregiver summary `games_played` incremented (5) |
| Rate limiting | ✓ (dev) | Middleware present; 100 req/min enforced only when `rate_limit_enabled` (auto-on in production, off in dev by default). UI already renders 429 + banner |

### Endpoint Configuration

| Aspect | Status | Details |
|---------|--------|---------|
| API URLs | ✓ | Mobile `ApiService` uses same `/api/v1` paths as web dashboard `_Api` — verified line-by-line: roster, summary, acknowledge, schedules, audit |
| Authentication | ✓ | JWT Bearer; refresh-retry-once implemented in `ApiService._send` (api_service.dart:115-120) |
| Authorization | ✓ | RBAC entirely server-side: cross-roster 403, unlinked-patient 404, invalid enum 422. Client never enforces access |
| Middleware | ✓ | CORS allows the web client; rate limiter registered |

### Request/Response Flow

| Test | Status | Result |
|------|--------|--------|
| No auth token | ✓ | 401 on all protected endpoints |
| Garbage token | ✓ | 401 |
| Other caregiver's roster | ✓ | 403 (server linkage enforced) |
| Unlinked patient summary | ✓ | 404 |
| Bad UUID path param | ✓ | 422 with structured pydantic detail |
| Invalid reminder_type | ✓ | 422 (enum validation) |
| Ack nonexistent alert | ✓ | 404 |

### Authentication & Authorization

| Aspect | Status | Details |
|---------|--------|---------|
| JWT access token | ✓ | Login → token works on every endpoint |
| Refresh flow | ✓ | 200, new access token issued |
| Refresh rotation | ⚠️ | Old refresh token remains valid after use — see Issues #1 |
| Role-based tier gating | ✓ | Summary strips clinical fields (accuracy/trends/flags) for basic tier — client reflects, doesn't enforce |

### Data Persistence

| Test | Status | Details |
|------|--------|--------|
| Schedule create→read | ✓ | Created schedule appears in patient's schedule list (5 rows incl. new) |
| Schedule delete | ✓ | Row deactivated (soft delete); no longer active in list |
| Game telemetry | ✓ | session → action → complete returns computed accuracy; summary reflects new game count |
| Data flow patient→caregiver | ✓ | Patient-side writes visible in caregiver-side reads within the same DB |

### Error Handling

| Test | Status | Details |
|------|--------|--------|
| Consistent error shape | ✓ | `{"detail": ...}` across 401/403/404/422 |
| 429 handling in client | ✓ | Screen maps 429 → gold banner + retry copy (no silent failure) |
| Retry logic | ✓ | Client retries once after refresh on 401 (api_service.dart:115-120) |
| User-facing messages | ✓ | Per-tier honest states ("admin-only", "unavailable right now") instead of fake data |

### Issues Found

| # | Issue | Severity | Recommendation |
|---|--------|----------|----------------|
| 1 | Refresh tokens are not rotated/revoked on use — a leaked refresh token is valid indefinitely | Medium | Revoke the old refresh token when issuing a new one (single-use rotation) |
| 2 | `CORS_ORIGINS` defaults to `*` with credentials in play | Low (dev) / Medium (prod) | Set an explicit origin list in production env |
| 3 | No `admin` or `asha_worker` demo account exists — audit view and multi-patient switcher could not be exercised end-to-end with real credentials | Low | Seed one admin + one ASHA worker with 2+ linked patients in `seed_demo.py` |
| 4 | No persistent request-level log file observed for failed integrations (logging goes to stdout) | Low | Route uvicorn/app logs to a file in production for audit trail |

### Recommendations

1. **Refresh-token rotation** — one-line revocation on refresh closes Issue #1
2. **Seed admin/ASHA demo accounts** — lets the audit card and the multi-patient switcher be demoed truthfully
3. **Production CORS** — explicit origins once a real web domain exists
4. **Integration test for the schedule lifecycle** — the create→list→delete flow is the only write path from mobile; a pytest case would pin the contract

### Overall Status

**Status:** passed

**Summary:** All seven dashboard views integrate against the same backend endpoints the web dashboard uses, with zero parallel API logic. Auth, RBAC (server-side), tier gating, persistence, and error contracts verified live with real credentials; patient-side telemetry correctly flows into caregiver-side reads. Four non-blocking issues documented, none affecting demo correctness.

---

*Integration verification: 2026-09-06T15:30:00Z*
_Verifier: Claude (gsd-integration-checker)_
