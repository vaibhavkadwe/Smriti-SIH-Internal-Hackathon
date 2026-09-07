# Client-Side Game Analytics / Telemetry — Design Research

**Date:** 2026-09-07
**Scope:** elder-care mobile games (Match It, Routine Sequencing) and the caregiver dashboard that consumes their analytics. Primary sources only — every claim is cited by file:line.

---

## 1. Current state of analytics/telemetry in the codebase

### 1.1 `mobile/lib/games/game_analytics_engine.dart` — exists, fully written

The file does exist (`/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/mobile/lib/games/game_analytics_engine.dart`, 239 lines, 8.5 KB). It is described as "Inline adaptive-difficulty engine and telemetry for the cognitive games" (line 1) and is "Pure Dart (no Flutter imports) so rules are unit-testable" (line 8).

**`CognitiveGameSession` (lines 16-63)** — per-session record:

```dart
class CognitiveGameSession {
  final String sessionId;
  final String patientId;
  final String gameType; // 'match_it' | 'routine_sequencing'
  final int difficultyLevel; // 1 | 2 | 3
  final int timeTakenInSeconds;
  final int totalAttempts;
  final int correctMoves;
  final int incorrectMoves;
  final bool isCompleted;
  final int stuckDurationSeconds; // longest gap without a correct move
  final int avgResponseTimeMs;
  final DateTime playedAt;
  ...
  double get accuracyPct =>
      totalAttempts > 0 ? (correctMoves / totalAttempts) * 100 : 0.0;
```

`toJson()` (lines 48-62) emits: `session_id`, `patient_id`, `game_type`, `difficulty_level`, `time_taken_s`, `total_attempts`, `correct_moves`, `incorrect_moves`, `is_completed`, `stuck_duration_s`, `avg_response_time_ms`, `accuracy_pct`, `played_at`.

**`ReportTag` enum (lines 67-76)** — fixed set: `maintainLevel`, `raiseLevel`, `lowerLevel`, `strongRecall`, `needsSupport`, `attentionLag`, `routineStable`, `quickResponse`.

**`GamePerformanceReport` (lines 79-116)** — what feeds the dashboard:

```dart
class GamePerformanceReport {
  final String patientId;
  final String gameType;
  final int difficultyLevel;
  final double accuracyScore; // 0-100
  final double cognitiveSpeedScore; // 0-100 (100 = fastest band)
  final double attentionScore; // 0-100 (penalises stuck time)
  final int recommendedNextLevel;
  final List<ReportTag> tags;
  ...
```

`toJson()` (lines 100-112) emits `accuracy_score`, `cognitive_speed_score`, `attention_score`, `recommended_next_level`, `tags`, and the two **dashboard trend-chart fields**: `accuracy_pct` (== `accuracyScore`) and `avg_response_time_ms` (line 111, derived from `_speedToResponseMs()` at line 114: `(6000 * (1 - (cognitiveSpeedScore / 100))).round().clamp(500, 12000)`).

**`GameAnalyticsEngine` (lines 127-239)** — singleton; rule thresholds (lines 132-150):

```dart
static const int stuckHintSeconds = 15;
static const double lowAccuracyPct = 40.0;
static const double highAccuracyPct = 85.0;
static const double slowCompletionFactor = 1.5;
static const int sessionsBeforeChange = 2;     // TWO-consecutive agreement

static const Map<String, Map<int, int>> _levelTargets = {
  'match_it':          {1: 90,  2: 150, 3: 240},
  'routine_sequencing':{1: 45,  2: 70,  3: 120},
};

static const Map<int, int> incorrectMovesHintThreshold = {1: 3, 2: 4, 3: 5};
```

- `evaluate(CognitiveGameSession s)` (lines 156-195) — computes `accuracy`, `speed`, `attention` (formula at lines 168-170: `100 - (stuckDurationSeconds / 15) * 20`, clamped 0-100), assigns tags, returns report.
- `recommendedLevel(CognitiveGameSession s)` (lines 199-213) — applies **2 consecutive agreeing verdicts** before a level moves, clamped 1-3.
- `_verdict(CognitiveGameSession s)` (lines 216-226) — single-session verdict: `-1` if `accuracyPct < 40.0` OR slow; `+1` if `accuracyPct > 85.0` AND completed AND `timeTakenInSeconds < target`; else `0`.
- `shouldHintNow({secondsSinceLastCorrect, incorrectMoves, difficultyLevel})` (lines 229-235) — per-tick hint trigger.
- `reset()` (line 238) — used by tests / caregiver override.

> The Dart engine and the Python `difficulty_engine.py` use different thresholds (40/85 + 2-session vs 50/85 + 3/2-session). Comment at line 131 says the Dart values are "also mirrored in backend difficulty_engine.py" — but the backend uses different numbers (see §3). The Dart side is the source of truth for the in-app hint and the level adjust shown in the session report.

### 1.2 Where the engine is wired in the mobile app

Grep across `mobile/lib/`:

- `mobile/lib/screens/match_it_screen.dart:6` — `/// Telemetry: every flip is buffered and POSTed fire-and-forget to…`
- `mobile/lib/screens/match_it_screen.dart:21` — `import '../games/game_analytics_engine.dart';`
- `mobile/lib/screens/match_it_screen.dart:61` — `final GameAnalyticsEngine _engine = GameAnalyticsEngine.instance;`
- `mobile/lib/screens/match_it_screen.dart:131` — `// Telemetry` section header.
- `mobile/lib/screens/match_it_screen.dart:173` — `// One stuck telemetry event per idle episode; rearmed on next tap.`
- `mobile/lib/screens/routine_screen.dart:6` — `/// Telemetry: every placement is buffered and POSTed fire-and-forget to…`
- `mobile/lib/screens/routine_screen.dart:20` — `import '../games/game_analytics_engine.dart';`
- `mobile/lib/screens/routine_screen.dart:56` — `final GameAnalyticsEngine _engine = GameAnalyticsEngine.instance;`
- `mobile/lib/screens/routine_screen.dart:117` — `// Telemetry` section header.

So the engine instance is already held by both game screens, and they both have explicit "Telemetry" sections in their code.

### 1.3 `GameAction` / `GameSession` — server model (`backend/app/models/all_models.py`)

**`GameSession` (lines 58-75):**

| Column | Type | Notes |
|---|---|---|
| `id` | `UUID` PK | |
| `patient_id` | `UUID` FK → patients | |
| `game_type` | `Enum(GameTypeEnum)` | `match_it` / `routine_sequencing` |
| `difficulty_level` | `Integer` default 1 | |
| `content_pack_id` | `String(100)` nullable | Match It |
| `routine_id` | `String(100)` nullable | Routine Sequencing |
| `started_at` | `DateTime` | |
| `completed_at` | `DateTime` nullable | |
| `attempts` | `Integer` default 0 | |
| `correct_count` | `Integer` default 0 | |
| `incorrect_count` | `Integer` default 0 | |
| `accuracy_pct` | `Float` nullable | |
| `avg_response_time_ms` | `Float` nullable | |
| `raw_event_log` | `JSON` nullable | appended per action |
| `created_at` | `DateTime` | |

**`DifficultyAdjustmentLog` (lines 77-87):** `id`, `patient_id`, `game_type`, `old_difficulty`, `new_difficulty`, `reason`, `adjusted_at`, `triggered_at`.

There is **no separate `GameAction` table** on the server. Per-action events are appended to `GameSession.raw_event_log` (a JSON array). `game_service.py:49` initialises `raw_event_log=[]`; `game_service.py:103-107` reassigns (per CLAUDE.md "raw_event_log reassigned so SQLAlchemy persists it"):

```python
# Append to raw_event_log (JSONB array). Reassign — don't mutate — so
updated_log = list(session.raw_event_log or [])
...
session.raw_event_log = updated_log
```

Server-side final metrics are recomputed on `complete_game_session` from `raw_event_log` (`game_service.py:134-152`):
- `avg_response_time_ms` from per-action response times,
- `accuracy_pct` from per-action correctness,
- then the `GameSession` row is updated with both.

### 1.4 `backend/app/routes/games.py` — endpoints

From the module docstring (lines 1-14) and the file:

- `POST /games/sessions` (line 168) — start a session; `require_patient`; consent scope `game_data`; returns `{session_id, started_at}`.
- `POST /games/sessions/{session_id}/actions` (line 208) — record one action; payload `{action_type, action_data, is_correct?, response_time_ms?}` (`RecordActionRequest`, lines 78-83).
- `POST /games/sessions/{session_id}/complete` (line 230) — `require_patient`; returns `SessionSummaryResponse{total_attempts, correct_count, incorrect_count, accuracy_pct, avg_response_time_ms, …}`.
- `GET /games/sessions/{session_id}` (line 242) — viewer + access check + read-audit.
- `GET /games/patients/{patient_id}/history` (line 262) — clinical tier only.
- `GET /games/patients/{patient_id}/stats` (line 283) — clinical tier only; aggregates `accuracy_pct` and `avg_response_time_ms` **per day** over a window (default 14d, max 90) and returns a `daily_trends` list plus overall.
- `GET /games/content-packs` and `GET /games/content-packs/{pack_id}/board` (lines 359, 366).
- `POST /games/patients/{patient_id}/routine` and `GET /games/patients/{patient_id}/routine` (lines 419, 435).
- `GET /games/routine/board` (line 448).
- `POST /games/difficulty/evaluate` (line 465) — staff-only; calls the Python `difficulty_engine`.

Ownership guard: `_ensure_owned_session` (lines 45-64) ensures the calling patient owns the session before actions/complete; otherwise 403.

> **Implication for a client-side engine:** the live `POST /games/sessions/{id}/actions` and `complete` endpoints already compute everything the server needs from the per-action stream. The client engine should **send raw per-action events** (so the server's `raw_event_log` stays authoritative for analytics) and **treat the report it computes as a UI hint / fast preview**, not as a second source of truth.

---

## 2. How the offline outbox currently replays game data

### 2.1 `mobile/lib/services/offline_sync_service.dart` (221 lines)

Library docstring (lines 1-15) describes the contract:

> game_session: create a fresh server session, replay the recorded actions (each is_correct / response_time_ms), then complete it so the server computes the same metrics as the online path.

Enqueue shape (lines 74-95) — `enqueueGameSession` writes a `SyncQueueItem` with `resourceType: 'game_session'`, `operation: 'create'`, and a `payload` containing `game_type`, `difficulty_level`, `content_pack_id`, `started_at`, `completed_at`, and a `actions: []` array built from each `GameAction.toJson()`.

Enqueue from local tables (lines 97-113) — `enqueueStoredUnsynced({patientId})` reads `db.getUnsyncedSessions()` and `db.getUnsyncedActions()` (filtered by `sessionId`), writes a sync item, then marks both session and actions synced.

`syncNow()` (lines 119-141) — guarded by `_syncing`; probes online via `language/status`; for each pending item calls `_replay`; on success marks synced; on exception marks failed with the error string; `clearSyncedItems(olderThanSeconds: 7 * 24 * 3600)` (line 136) honours the 7-day retention.

`_replayGameSession(item)` (lines 154-172) — this is the wire-level contract:

```dart
final sessionId = await api.startGame(
  gameType: payload['game_type'] as String? ?? 'match_it',
  difficultyLevel: payload['difficulty_level'] as int? ?? 1,
);
final actions = (payload['actions'] as List? ?? const [])
    .cast<Map<String, dynamic>>();
for (final action in actions) {
  await api.recordGameAction(
    sessionId: sessionId,
    actionType: action['action_type'] as String? ?? 'tap',
    actionData: action['action_data'] as Map<String, dynamic>? ?? const {},
    isCorrect: action['is_correct'] as bool?,
    responseTimeMs: action['response_time_ms'] as int?,
  );
}
await api.completeGame(sessionId);
```

So the offline path replays **start → record-action × N → complete** through the same live endpoints; the server therefore sees the same `raw_event_log` regardless of online/offline. The completed server session gets its `accuracy_pct` and `avg_response_time_ms` from that log, identically.

`_replayReminderAck(item)` (lines 174-184) — calls the live ack endpoint; 404 is treated as "event never delivered" and dropped.

`_pushGeneric(item)` (lines 186-206) — pushes everything else to `POST /api/v1/sync` with the outbox shape `{patient_id, items: [{resource_type, operation, resource_id, payload}]}`.

`start({interval = 30s})` (lines 212-214) and `stop()` (lines 216-219) — periodic timer.

### 2.2 `mobile/lib/database/app_database.dart` (drift) — local tables

**`GameSessions` (lines 33-48):**

| Column | Type | Notes |
|---|---|---|
| `id` | `text` PK | session uuid |
| `patient_id` | `text` | |
| `game_type` | `text` | `match_it` / `routine_sequencing` |
| `difficulty_level` | `integer` default 1 | |
| `attempts` | `integer` default 0 | |
| `correct_count` | `integer` default 0 | |
| `incorrect_count` | `integer` default 0 | |
| `avg_response_time_ms` | `real` nullable | |
| `started_at` | `dateTime` | |
| `completed_at` | `dateTime` nullable | |
| `synced` | `boolean` default false | |

Note: no `accuracy_pct`, no `raw_event_log` locally — the client doesn't pre-compute that.

**`GameActions` (lines 51-64):**

| Column | Type | Notes |
|---|---|---|
| `id` | `text` PK | |
| `session_id` | `text` FK → GameSessions | |
| `action_type` | `text` | `tap`, `match`, `place`, … |
| `action_data` | `text` (JSON string) | |
| `is_correct` | `bool` nullable | |
| `response_time_ms` | `int` nullable | |
| `timestamp` | `dateTime` | |
| `synced` | `bool` default false | |

**`SyncQueue` (lines 84-98):** `id` PK, `patient_id?`, `resource_type`, `operation`, `resource_id`, `payload` (JSON), `created_at`, `synced_at`, `retry_count`, `last_error`.

Helpers (lines 143-204) — `getUnsyncedSessions()`, `markSessionSynced`, `getUnsyncedActions()` (ordered by timestamp ASC), `markActionSynced`, `enqueueSyncItem`, `pendingSyncItems(limit:200)`, `markSyncItemSynced`, `markSyncItemFailed`, `clearSyncedItems(olderThanSeconds: 0)`.

### 2.3 Backend sync contract

`backend/app/routes/sync.py` exposes only `POST /sync` (line 49) and `GET /sync/pending/{patient_id}` (line 99). `SyncItem` (lines 33-39): `resource_type`, `operation`, `resource_id` (UUID), `payload: dict`, `created_at?`. `SyncBatchRequest` (lines 41-43): `patient_id` + `items: List[SyncItem]`.

Resource-type enums are validated up front (lines 62-76): `SyncResourceTypeEnum` (`game_session`, `reminder_event`, `offline_symptom`) and `SyncOperationEnum` (`create`, `update`, `delete`). Result: `{patient_id, synced, errors}`.

`backend/app/services/sync_service.py` — `process_sync_batch` (lines 38-72) inserts a `SyncQueue` row per item with `synced_at=None` and returns `{synced, errors}`. `consume_sync_queue` (lines 85-149) only materialises `offline_symptom → SymptomLog`; everything else (including `game_session`) is **acked at the outbox** with the comment:

```python
# Replay-through-live-endpoint flows: acknowledge at the outbox.
counts["acked"] += 1
```

So the **server-side `SyncQueue` table is a pure outbox for symptom logs**; for game sessions, the offline replay path goes straight through `startGame` / `recordGameAction` / `completeGame` (see §2.1) and never lands in the server's `sync_queue` table.

> **Implication:** a client-side analytics engine that wants to surface risk flags / level-change recommendations to the dashboard offline should expose them via a column the **mobile** outbox already has — i.e. tag them in the action stream or attach them to the local `GameSession` row before the replay — not by introducing a new resource type on the server (which would require a new enum value, a new consumer branch, and a new outbox route).

---

## 3. Adaptive difficulty engine (sister file) — `backend/app/services/difficulty_engine.py`

The file (207 lines) defines an abstract `DifficultyStrategy` (lines 20-46) and a single concrete `RuleBasedDifficultyStrategy` (lines 48-111).

**Thresholds (lines 52-61):**

```python
BUMP_THRESHOLDS = {
    "consecutive_high_accuracy": 3,  # 3 consecutive sessions > 85%
    "high_accuracy_pct": 85.0,
    "response_time_threshold_ms": 8000,  # bump if avg < 8 sec
}

DROP_THRESHOLDS = {
    "consecutive_low_accuracy": 2,  # 2 consecutive sessions < 50%
    "low_accuracy_pct": 50.0,
}
```

**`calculate_adjustment(...)` (lines 63-87):**
- Bump: 3 consecutive sessions with `accuracy_pct > 85.0`; only if `current_difficulty < 3`.
- Drop: 2 consecutive sessions with `accuracy_pct < 50.0`; only if `current_difficulty > 1`.
- `None` = no change.

`_check_bump_rule` (lines 89-99) and `_check_drop_rule` (lines 101-111) — both scan `recent_sessions[:5]` (max 5 most recent). A streak is broken as soon as one session fails the predicate; **the scan does not require sessions to be strictly consecutive in calendar time**, just in list order (newest first, since `get_recent_sessions` orders by `completed_at desc`).

`get_recent_sessions(db, patient_id, game_type, days_back=30, limit=20)` (lines 114-138) — filters `completed_at IS NOT NULL`, `>= now-30d`, ordered `desc`, limit 20.

`evaluate_difficulty(db, patient_id, game_type, current_difficulty, strategy=None)` (lines 141-181) — entry point used by `POST /games/difficulty/evaluate`. Returns `{new_difficulty, reason, rule_triggered, recent_sessions_reviewed}`. When a level change is decided, calls `_log_adjustment` to write a `DifficultyAdjustmentLog` row (lines 184-202).

> **Note on the divergence with the Dart engine (see §1.1).** The two engines disagree on:
> 1. The "low" threshold: Dart `40.0` vs Python `50.0`.
> 2. The bump streak length: Dart 2 vs Python 3.
> 3. The drop streak length: Dart 2 vs Python 2 (agree).
> 4. The "slow" rule: Python never uses a slow factor for the verdict, only `response_time_threshold_ms: 8000` (declared but not referenced in `_check_bump_rule`/`_check_drop_rule`).
>
> The docstring in `game_analytics_engine.dart:131` says the Dart constants are "also mirrored in backend difficulty_engine.py" — they are not. Decide and align (or document the split: Dart is the in-app hint, Python is the historical / cross-device authority).

---

## 4. What metrics the caregiver dashboard reads

### 4.1 `backend/app/routes/dashboard.py`

Two endpoints:
- `GET /dashboard/caregivers/{caregiver_id}/patients` (line 19) — roster.
- `GET /dashboard/patients/{patient_id}/summary` (line 40) — the headline endpoint.

`get_patient_summary` (lines 41-64) does access check + read-audit, then `DashboardService.get_patient_summary(...)`, then **strips clinical fields when tier != 'clinical'** (lines 55-61):

```python
if tier != "clinical":
    summary.pop("accuracy_pct", None)
    summary.pop("avg_response_time_ms", None)
    summary.pop("clinical_flags", None)
    summary.pop("daily_trends", None)
    summary.pop("accuracy_drop_pct", None)
    summary["view"] = "basic"
else:
    summary["view"] = "clinical"
```

So the dashboard summary's **`accuracy_pct` and `avg_response_time_ms` are clinical-tier-only** and travel inside the same summary payload as `compliance_pct`, `games_played`, `reminders_acknowledged`, `reminders_total`, `reminders_missed`, `active_alerts[]`, `clinical_flags{cognitive_drop_detected, high_missed_reminders}`, and `daily_trends[]`. The 14-day per-day trend is built from `daily_trends` (line 59).

Also relevant: `GET /games/patients/{patient_id}/stats` (`backend/app/routes/games.py:283-356`) builds a 14-day trend with `accuracy_pct` + `avg_response_time_ms` per day and an `overall` aggregate — this is the **clinical-tier** feed the dashboard's sparklines could pivot to instead of summary. It is audited and gated by `ensure_clinical_access` + `ensure_consent(game_data)`.

### 4.2 `mobile/lib/screens/caregiver_dashboard_screen.dart`

The mobile caregiver dashboard (804 lines) consumes the summary endpoint. Relevant pieces:

- **Cognitive accuracy tile** (lines 486-493) — clinical only; reads `summary['accuracy_pct']` as a percent, subtitle `'$games games (7d)'` from `summary['games_played']` (line 481).
- **Compliance tile** (lines 494-495) — `summary['compliance_pct']`, `$ack/$total` from `summary['reminders_acknowledged']` and `summary['reminders_total']`.
- **Missed tile** (lines 496-497) — `summary['reminders_missed']`; coral if > 0 else gold.
- **Trends section** (lines 512-555, `_trends`) — two `TrendChart`s: "Accuracy trend (14d)" from `trends` items' `accuracy_pct` and "Response time trend (14d)" from `trends` items' `avg_response_time_ms`. If the server returned an empty list, shows a `tintGold` lock card explaining "Basic view — accuracy and response-time trends are visible to linked clinical staff only."
- **Alerts / clinical flags** (lines 393-476) — two surfaces: `active_alerts[]` rendered as tinted cards with severity chips, and threshold banners from `clinical_flags.cognitive_drop_detected` and `clinical_flags.high_missed_reminders`. The drop copy is hard-coded: `'Cognitive drop detected (<60% accuracy)'` (line 460).
- **Compliance log** (lines 558-632) — today's reminder events with status chips (DONE / ESCALATED / MISSED).
- **Schedules** (lines 635-712) — add/delete list.
- **Audit** (lines 716-770) — `auditLogs(limit: 50)` from `ApiService`, admin-only.

> **Implication for the analytics engine:** the dashboard's visible contract is just `(accuracy_pct, avg_response_time_ms)` per day + an "is a cognitive drop happening" boolean. Any new client-computed signal either (a) feeds those two numbers (preferred — no schema change) or (b) needs a new summary key + a server-side `clinical_flags` extension.

---

## 5. DESIGN.md constraints that affect this work

`/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/DESIGN.md` (430 lines). Key constraints:

- **Body floor (line 442):** "patient-facing strings use `--text-body-lg` (20px) minimum. 14–16px sizes are reserved for metadata and captions." So if the analytics engine ever surfaces a number or label to the patient, it must be ≥ 20px in the mobile theme.
- **Card-face tints (line 437):** "Coral, Sky Blue, Mint, Gold at ≤25% opacity over Parchment, illustration surfaces only (memory-match faces, routine cards)." The engine should never paint a card face in a way that violates the tint rules; analytics tiles follow the standard tile pattern (40px radius, no shadow, hairline Ash border per line 144 / "Don't apply drop shadows to cards", line 192).
- **Contrast (line 447):** "Off-Black (#242424) text/icons on any tint above must meet WCAG AA (4.5:1). All four tints at ≤25% over Parchment exceed 10:1." The mobile dashboard already uses the periwinkle / coral / gold tints for alerts (e.g. lines 408, 448) — match the pattern; do not introduce new accent fills.
- **Type pairing (line 236):** "ABC Diatype Mono … all body copy, navigation, button labels, badges, tags, and inline UI text." Analytics tags / chips must be mono, uppercase, 12-14px (per "tag" pattern at line 139: "12px 20px padding, 14px mono uppercase"). The `ReportTag` names in `game_analytics_engine.dart:67-76` are snake-case Dart names — when displayed in the UI, the screen already needs to map them to human strings (e.g. "Strong recall", "Needs support"); the engine itself only stores the enum names.
- **Pill / soft-rect rule (line 193):** "Never use corner radii below 16px on cards or below 100px on buttons." Existing tiles use `Monad.radiusCard` (40px, line 786) and `Monad.radiusPill` (lines 344, 9999px) — keep the same.
- **No new accent colours (line 194):** "Never introduce additional accent colors for UI elements — the pastel palette (Sky, Mint, Coral, Gold) is decorative-only and belongs in illustrations and gradient washes." Do not invent a "risk red" outside `#f37a0a` (Crimson) or `#ff9473` (Coral). The existing dashboard already uses `Monad.crimson` for the trend-down icon (line 459) — reuse it.
- **Spacing base unit (line 68):** 8px; section gap 64px; element gap 16px; card padding 40px. Engine summary widgets, if added, should follow the same rhythm (12-16-24 spacing between tiles, matching `_metrics` line 502-507).

---

## Design recommendation (≤ 8 bullets)

1. **The Dart engine already exists and is wired into both game screens** (`game_analytics_engine.dart` 1-239, instantiated at `match_it_screen.dart:61` and `routine_screen.dart:56`). Treat the existing `GameAnalyticsEngine` as the canonical client-side scorer — extend it, do not duplicate it.
2. **Do not push a new `analytics_report` resource type through the server.** The server's `SyncQueue` consumer only materialises `offline_symptom`; everything else is replayed through live endpoints (`sync_service.py:108-138`). The offline outbox path is `start → recordAction × N → complete` (`offline_sync_service.dart:154-172`), so a client can already drive a complete server-side session without an explicit report payload.
3. **Keep the server's `raw_event_log` authoritative.** Per-action replay is the wire format. The client should keep emitting `GameAction` rows with `is_correct` and `response_time_ms` (drift table `GameActions`, `app_database.dart:51-64`) and let `game_service.complete_game_session` compute `accuracy_pct` and `avg_response_time_ms` server-side (`game_service.py:134-152`). The Dart report is a **UI hint**, not a second metric.
4. **The client engine should send the report it computes only to the patient UX (hint timing, level-adjust banner) and to the caregiver dashboard via the existing `summary` endpoint.** No new field on `GameSession` is needed; if a new risk flag is required, surface it through the existing `clinical_flags` block on the server summary and let the client mirror the boolean in `_alerts` (`caregiver_dashboard_screen.dart:393-476`).
5. **Align the Dart and Python thresholds or document the split.** The Dart thresholds (40/85, 2-session bump, 2-session drop) and the Python thresholds (50/85, 3-session bump, 2-session drop) are inconsistent (`game_analytics_engine.dart:132-137` vs `difficulty_engine.py:52-61`). The comment at `game_analytics_engine.dart:131` claiming they are "mirrored" is false. Either: (a) sync them, or (b) document explicitly that the Dart engine is the in-session hint source and the Python engine is the historical authority.
6. **For offline risk detection, extend the local `GameSessions` drift row** with the per-session `tags` and `recommendedNextLevel` produced by the engine (`app_database.dart:33-48`) so a queued session carries its client verdict. Do not invent a new sync payload — the existing `enqueueGameSession` will replay everything (`offline_sync_service.dart:74-95`).
7. **In the patient UX, follow DESIGN.md patient-facing constraints:** body strings ≥ 20px (`DESIGN.md:442`); never shadow tiles (`DESIGN.md:192`); use only Lake Blue for one primary action and tint cards with the four pastels at ≤25% (`DESIGN.md:437, 447`); tags/chips stay 12-14px mono uppercase (`DESIGN.md:139`).
8. **Surface the existing `attentionScore` and `cognitiveSpeedScore` from `GamePerformanceReport`** as supplementary values on the patient "end of session" card and as **second-axis** entries on the caregiver trend chart if/when the dashboard trend widget grows a dual line. The fields are already emitted by the engine's `toJson()` (`game_analytics_engine.dart:100-112`) and just need a downstream consumer — no new model fields required.

Skipped (deliberate, for later): a separate "anomaly detector" rule layer (overlap with `AlertTriggerTypeEnum.COGNITIVE_SCORE_DIP`), ML-based difficulty strategy (already noted as v2 in `difficulty_engine.py:1-6`), and any on-device model of free-text voice analysis (separate companion surface).

---

## Files cited

- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/mobile/lib/games/game_analytics_engine.dart`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/mobile/lib/services/offline_sync_service.dart`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/mobile/lib/database/app_database.dart`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/mobile/lib/screens/match_it_screen.dart`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/mobile/lib/screens/routine_screen.dart`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/mobile/lib/screens/caregiver_dashboard_screen.dart`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/app/models/all_models.py`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/app/services/difficulty_engine.py`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/app/services/sync_service.py`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/app/services/game_service.py`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/app/routes/games.py`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/app/routes/sync.py`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/backend/app/routes/dashboard.py`
- `/Users/priyanujgoswami/Smriti-SIH-Internal-Hackathon/DESIGN.md`
