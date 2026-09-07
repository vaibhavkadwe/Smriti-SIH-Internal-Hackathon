# Graph Report - Smriti-SIH-Internal-Hackathon  (2026-09-07)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 3117 nodes · 7055 edges · 142 communities (94 shown, 38 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 586 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d086ead8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app_database.dart
- live-browser.js
- resumeSession
- game_models.dart
- all_models.py
- RAGService
- setLiveState
- dashboard/lib/main.dart
- mobile/lib/theme/monad_theme.dart
- ReminderEvent
- User
- modern-screenshot.umd.js
- dashboard/lib/theme/monad_theme.dart
- shared_models.dart
- el
- ReportService
- initPageChat
- GameSession
- api_service.dart
- notification_service.py
- jobs.py
- test_phase2_services.py
- match_it_screen.dart
- initGlobalBar
- games.py
- mobile/lib/main.dart
- Phase 1 Plan: Repository Scaffold + Data Models
- game_analytics_engine.dart
- routine_screen.dart
- VoiceCompanionService
- LLMClient
- caregiver_dashboard_screen.dart
- sync.py
- patients.py
- app.js
- package:flutter/material.dart
- language.py
- reports.py
- game_visuals.dart
- match_it_service.dart
- reminders_screen.dart
- routine_service.dart
- voice_companion_screen.dart
- showToast
- handleManualEditActivity
- voice_companion.py
- test_language_service.py
- BaselineData
- captureElementToBlob
- offline_sync_service.dart
- auth_session.dart
- reminders.py
- AuthService
- test_phase12_gates.py
- ConversationStore
- auth.py
- AdaptiveEngine
- test_retention_service.py
- ApiService
- models.py
- AppDelegate
- resolveLiveInjectionAnchor
- pack_picker_screen.dart
- createLiveBrowserSessionState
- generate_match_it_board
- onAnnotDown
- dashboard.py
- PerformanceTracker
- createLiveBrowserDomHelpers
- reminder_scheduler.dart
- LanguageServiceError
- deps.py
- test_api_routes.py
- TestStartingDifficulty
- DataClass
- get_db
- TestAdaptiveDecisions
- scheduleAcceptCleanup
- models/shared_models.dart
- main.py
- RateLimitMiddleware
- .hash_password
- dashboard/web/manifest.json
- mobile/web/manifest.json
- local_content_packs.dart
- extract_document_text
- TestPerformanceTracker
- test_document_upload.py
- test_phase5_game_stats.py
- live-browser-ignores.js
- @DataClassName
- dev_role_menu.dart
- impeccable
- smoke_e2e.py
- app_config.dart
- game_labels.dart
- 0001_initial_schema.py
- opencode.json
- FlutterActivity
- graphify.js
- app/__init__.py
- JWT Auth (access 15min + refresh 7d)
- Docker Compose local dev stack (pgvector + Redis + backend)
- get
- get
- post
- get
- post
- get
- post
- get
- post
- get
- post
- get
- post
- get
- post
- get
- post
- get
- post
- get
- post
- delete
- BhashiniProvider
- Pydantic Schemas
- PatientProfile
- ReminderSchedule
- bool?
- DateTime
- Exception

## God Nodes (most connected - your core abstractions)
1. `User` - 100 edges
2. `PatientProfile` - 55 edges
3. `GameSession` - 47 edges
4. `ReminderEvent` - 41 edges
5. `GameTypeEnum` - 40 edges
6. `ReminderService` - 40 edges
7. `ComplianceService` - 38 edges
8. `LLMClient` - 35 edges
9. `RAGService` - 35 edges
10. `ReminderStatusEnum` - 35 edges

## Surprising Connections (you probably didn't know these)
- `deactivate_schedule()` --references--> `_delete`  [EXTRACTED]
  backend/app/routes/reminders.py → dashboard/lib/main.dart
- `t_difficulty_import()` --uses--> `DifficultyStrategy`  [INFERRED]
  backend/test_phase2_services.py → backend/app/services/difficulty_engine.py
- `get_latest_weekly_report()` --references--> `_get`  [EXTRACTED]
  backend/app/routes/reports.py → dashboard/lib/main.dart
- `complete_game()` --references--> `_post`  [EXTRACTED]
  backend/app/routes/games.py → dashboard/lib/main.dart
- `create_content_pack()` --references--> `_post`  [EXTRACTED]
  backend/app/routes/games.py → dashboard/lib/main.dart

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Backend Services** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_auth_service, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_sync_service, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_language_service_provider [EXTRACTED 1.00]
- **Phase 1 Backend Services (auth + language + sync)** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_auth_service_jwt, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_language_service_provider, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_sync_service [EXTRACTED 1.00]
- **Compliance Trio (DPDP)** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_dpdp_compliance, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_consent_record_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_audit_log_model [EXTRACTED 1.00]
- **Data Model Layer** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_user_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_patient_profile_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_caregiver_patient_link_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_consent_record_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_audit_log_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_game_session_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_reminder_schedule_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_reminder_event_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_alert_flag_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_sync_queue_model [EXTRACTED 1.00]
- **Phase 1 Data Model Layer** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_user_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_consent_record_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_audit_log_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_patient_profile_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_caregiver_patient_link_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_game_session_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_reminder_models, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_alert_flag_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_sync_queue_model [EXTRACTED 1.00]
- **DPDP Act 2023 compliance (consent + audit + encryption)** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_decision_dpdp_compliance, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_consent_record_model, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_audit_log_model [EXTRACTED 1.00]
- **Phase 1 Infrastructure (FastAPI + Alembic + Docker + Flutter)** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_fastapi_skeleton, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_alembic_migrations, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_docker_compose_stack, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_flutter_skeleton [EXTRACTED 1.00]
- **Infrastructure Stack** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_fastapi, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_sqlalchemy, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_alembic, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_postgresql, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_redis, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_docker_compose [EXTRACTED 1.00]
- **Phase 1 Locked Decisions (8 items)** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_decision_mvp_cognitive_baseline, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_decision_caregiver_dashboard, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_decision_offline_first_gaming, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_decision_voice_companion, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_decision_reminder_escalation, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_decision_multilingual_mvp, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_decision_jwt_auth, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_decision_dpdp_compliance [EXTRACTED 1.00]
- **Phase 1 Decisions Set** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_mvp_cognitive_baseline, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_offline_first, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_voice_companion, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_reminder_escalation, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_multilingual_mvp, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_auth_jwt, docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_dpdp_compliance [EXTRACTED 1.00]

## Communities (142 total, 38 thin omitted)

### Community 0 - "app_database.dart"
Cohesion: 0.01
Nodes (158): BoolColumn get, class PatientRoutineRow extends, class ReminderEventRow extends, ColumnFilters, ColumnOrderings, dart:io, DateTimeColumn get, GeneratedColumn (+150 more)

### Community 1 - "live-browser.js"
Cohesion: 0.03
Nodes (123): addManualContextText(), applyGlobalBarLabelState(), applyPlaceholderSizingStyles(), bindEditBadgeProxy(), bufferToBase64(), buildCollapsible(), buildColorModels(), buildInsertPlaceholderSnapshotFromDom() (+115 more)

### Community 2 - "resumeSession"
Cohesion: 0.06
Nodes (87): applyParamDefaults(), applyParamValue(), applyPlaceholderDimensions(), applySavedSessionMeta(), clampVariantIndex(), clearHandled(), closedClipPath(), closeTunePopover() (+79 more)

### Community 3 - "game_models.dart"
Cohesion: 0.03
Nodes (78): accuracyPct, actionData, actionType, _artKeyFor, avgResponseTimeMs, cardId, cards, completedAt (+70 more)

### Community 4 - "all_models.py"
Cohesion: 0.08
Nodes (61): Alembic environment configuration for Elder-Care platform., Run migrations in 'offline' mode — emits SQL to stdout., Run migrations against a live database., run_migrations_offline(), run_migrations_online(), AcknowledgmentMethodEnum, AlertSeverityEnum, CaregiverPatientLink (+53 more)

### Community 5 - "RAGService"
Cohesion: 0.06
Nodes (53): _build_provider(), EmbeddingProvider, EmbeddingUnavailableError, get_embedding_provider(), HeuristicEmbeddingProvider, LocalSentenceTransformerProvider, OpenAIEmbeddingProvider, ABC (+45 more)

### Community 6 - "setLiveState"
Cohesion: 0.08
Nodes (71): abortSvelteComponentInjection(), applyEditing(), beginNewLiveConfiguration(), cancelEditing(), cancelEditingToPicking(), cancelInsertConfigure(), cleanup(), cleanupAcceptedSession() (+63 more)

### Community 7 - "dashboard/lib/main.dart"
Cohesion: 0.03
Nodes (69): _ack, acknowledge, _addSchedule, _addScheduleRow, _Api, _auditLogs, _auditPanel, _baseUrl (+61 more)

### Community 8 - "mobile/lib/theme/monad_theme.dart"
Cohesion: 0.03
Nodes (63): ash, blackPill, bluePill, cardPadding, cardShadow, cardShape, coral, crimson (+55 more)

### Community 9 - "ReminderEvent"
Cohesion: 0.10
Nodes (44): escalation_scan(), Escalate unacknowledged reminders, send reprompts, mark misses, raise alerts.…, ReminderEvent, ReminderSchedule, ReminderStatusEnum, ReminderTypeEnum, Digital Personal Data Protection (DPDP) Act 2023 & Encryption Service.…, Any (+36 more)

### Community 10 - "User"
Cohesion: 0.07
Nodes (50): Base, User, me(), ConsentCreateRequest, ConsentResponse, export_patient_data(), grant_consent(), list_audit_logs() (+42 more)

### Community 11 - "modern-screenshot.umd.js"
Cohesion: 0.09
Nodes (55): ae(), be(), bt(), Ce(), s(), Ct(), de(), dt() (+47 more)

### Community 12 - "dashboard/lib/theme/monad_theme.dart"
Cohesion: 0.04
Nodes (56): ash, blackPill, bluePill, cardPadding, cardShadow, cardShape, coral, crimson (+48 more)

### Community 13 - "shared_models.dart"
Cohesion: 0.04
Nodes (54): double?, acknowledgedAt, acknowledgmentMethod, attempts, avgResponseTimeMs, baselineFromApi, baselineToApi, cadence (+46 more)

### Community 14 - "el"
Cohesion: 0.07
Nodes (54): actionLabel(), applyConfigureBarChrome(), bindConfigureCountPillTooltip(), bindConfigureInlineControlHover(), bindConfigureModifierPillHover(), buildConfigureActionControl(), buildConfigureCountControl(), buildConfigureRow() (+46 more)

### Community 15 - "ReportService"
Cohesion: 0.07
Nodes (44): P7 — persisted weekly clinical summary (one per patient per week)., WeeklyReport, get_latest_weekly_report(), Most recent persisted weekly clinical report for a patient (falls back to…, EncryptionService, AES-256 Fernet-based field level encryption., Encrypt sensitive clinical text., Decrypt ciphertext back to plaintext. (+36 more)

### Community 16 - "initPageChat"
Cohesion: 0.08
Nodes (53): armPageChatForTyping(), attachSteerFocusDebug(), attachSteerFocusGuard(), buildSteerProcessingDots(), buildSteerQueueHint(), clearSteerAwaitTimer(), clearSteerFocusRecoverTimer(), collapsePageChat() (+45 more)

### Community 17 - "GameSession"
Cohesion: 0.09
Nodes (43): GameSession, GameTypeEnum, DifficultyStrategy, evaluate_difficulty(), get_recent_sessions(), _log_adjustment(), ABC, Any (+35 more)

### Community 18 - "api_service.dart"
Cohesion: 0.04
Nodes (50): dart:developer, int?, accessToken, acknowledgeAlert, acknowledgeReminder, ApiException, auditLogs, authToken (+42 more)

### Community 19 - "notification_service.py"
Cohesion: 0.09
Nodes (37): AlertFlag, NotificationDelivery, Base, UserDeviceToken, _build_provider(), ConsoleNotificationProvider, FCMNotificationProvider, get_notification_provider() (+29 more)

### Community 20 - "jobs.py"
Cohesion: 0.11
Nodes (34): alert_engine_pass(), generate_events(), main(), _next_sunday_midnight(), _periodic_loop(), AsyncSession, datetime, Background jobs — reminder escalation, sync consumption, retention. Implements… (+26 more)

### Community 21 - "test_phase2_services.py"
Cohesion: 0.06
Nodes (32): Rule-based difficulty adjustment using explicit thresholds., RuleBasedDifficultyStrategy, generate_routine_sequencing_board(), get_patient_routine(), Any, AsyncSession, UUID, Daily Routine Sequencing Game Service & Caregiver Routine Editor. Enables… (+24 more)

### Community 22 - "match_it_screen.dart"
Cohesion: 0.05
Nodes (41): MatchItCard, _api, _armStuckTimer, _bufferAndSend, _bufferedActions, build, card, cardBack (+33 more)

### Community 23 - "initGlobalBar"
Cohesion: 0.09
Nodes (39): agentHasWorkInFlight(), agentStatusText(), barPaletteForTheme(), brandMarkSvg(), buildDesignHeader(), buildParamsPanel(), cursorForInsertAxis(), designPanelCss() (+31 more)

### Community 24 - "games.py"
Cohesion: 0.07
Nodes (39): complete_game(), ContentItemIn, ContentPackCreate, ContentPackSummary, create_content_pack(), DifficultyEvaluationResponse, _ensure_owned_session(), GameHistoryItem (+31 more)

### Community 25 - "mobile/lib/main.dart"
Cohesion: 0.05
Nodes (40): CaregiverDashboardApp, TrendChart, RiskScreeningCard, FormState, _api, _AuthGate, _busy, _create (+32 more)

### Community 26 - "Phase 1 Plan: Repository Scaffold + Data Models"
Cohesion: 0.06
Nodes (40): Alembic Migrations, Alembic Migrations (SQLAlchemy 2.0 async), AlertFlag model (missed_reminders, cognitive_score_dip, activity_drop), AuditLog model (immutable read/write/delete audit), AuthService (bcrypt + JWT access 15min / refresh 7d), CaregiverPatientLink model (PermissionTierEnum basic/clinical), ConsentRecord model (DPDP consent capture), Decision: Caregiver dashboard as Flutter Web (shared Dart models) (+32 more)

### Community 27 - "game_analytics_engine.dart"
Cohesion: 0.05
Nodes (39): accuracyPct, accuracyScore, attentionScore, avgResponseTimeMs, CognitiveGameSession, cognitiveSpeedScore, correctMoves, difficultyLevel (+31 more)

### Community 28 - "routine_screen.dart"
Cohesion: 0.05
Nodes (36): ../games/game_analytics_engine.dart, ../games/game_labels.dart, ../games/game_visuals.dart, accent, _api, _armStuckTimer, _bufferAndSend, _bufferedActions (+28 more)

### Community 29 - "VoiceCompanionService"
Cohesion: 0.14
Nodes (26): VoiceCompanionConfig, activate_voice_config(), list_voice_configs(), List all voice companion system-prompt versions (oldest first)., Activate a previously created prompt version., Any, AsyncSession, Send a message to Claude; returns a dict with reply_text + metadata. (+18 more)

### Community 30 - "LLMClient"
Cohesion: 0.10
Nodes (27): detect_provider(), LLMClient, LLMServiceError, AsyncBaseTransport, Exception, Minimal LLM client shared by services (OpenRouter free tier or Anthropic). Used…, Drop paid slugs when free-only mode is on (OpenRouter only)., Return (url, headers, payload) for the active provider. (+19 more)

### Community 31 - "caregiver_dashboard_screen.dart"
Cohesion: 0.06
Nodes (34): _acknowledge, _addSchedule, _alerts, _api, _auditCard, build, _buildBody, _buildMain (+26 more)

### Community 32 - "sync.py"
Cohesion: 0.14
Nodes (29): SyncQueue, pending_sync_items(), AsyncSession, BaseModel, UUID, Offline-First Sync API Routes — batched offline events from mobile SyncQueue.…, Return unsynced queue items for a patient (synced_at IS NULL)., Persist offline-created events from the mobile device into the backend. Each… (+21 more)

### Community 33 - "patients.py"
Cohesion: 0.12
Nodes (29): _baseline(), CaregiverLinkRequest, CaregiverLinkResponse, create_patient(), _get_patient(), link_caregiver(), list_patient_caregivers(), PatientCreateRequest (+21 more)

### Community 34 - "app.js"
Cohesion: 0.10
Nodes (23): acknowledgeReminder(), acknowledgeReminderEvent(), checkCurrentUser(), closePatientPanels(), createReminderSchedule(), CULTURAL_ITEMS, flippedIndices, handleCardClick() (+15 more)

### Community 35 - "package:flutter/material.dart"
Cohesion: 0.07
Nodes (27): main, enterText, _loginAs, main, pump, pumpWidget, tap, GameAnalyticsEngine (+19 more)

### Community 36 - "language.py"
Cohesion: 0.10
Nodes (24): ASRRequest, _get_provider(), _handle(), language_status(), BaseModel, HTTPException, Speech & Language Translation API Routes. Routes wrap the configured language…, Translate between NER regional languages and English. (+16 more)

### Community 37 - "reports.py"
Cohesion: 0.12
Nodes (29): ensure_clinical_access(), ensure_consent(), get_permission_tier(), load_patient(), AsyncSession, UUID, Purpose-limitation gate: 403 unless an active ConsentRecord covers the scope., Resolve basic | clinical for this caller against this patient. (+21 more)

### Community 38 - "game_visuals.dart"
Cohesion: 0.07
Nodes (28): Color, CustomPainter, _TrendPainter, List, _assetDir, availableImages, color, CulturalArtPainter (+20 more)

### Community 39 - "match_it_service.dart"
Cohesion: 0.07
Nodes (29): double get, MatchItBoard, accuracyPct, attempts, board, cards, copyWith, correctMatches (+21 more)

### Community 40 - "reminders_screen.dart"
Cohesion: 0.07
Nodes (27): build, result, Map, _accentFor, _assameseFor, build, _buildCard, _buildSectionHeader (+19 more)

### Community 41 - "routine_service.dart"
Cohesion: 0.07
Nodes (28): int get, RoutineBoard, accuracyPct, board, canPlaceMore, copyWith, correctPlacements, errors (+20 more)

### Community 42 - "voice_companion_screen.dart"
Cohesion: 0.07
Nodes (28): _api, build, _ChatMessage, _companionAvatar, content, createState, dispose, _greeting (+20 more)

### Community 43 - "showToast"
Cohesion: 0.11
Nodes (26): abandonForeignSession(), applyOriginalAttrsToSvelteAnchor(), commitAcceptedSvelteComponentToDom(), componentModuleCandidates(), describeMountFailure(), detectDevServerBase(), discardOrphanedSession(), dismissToast() (+18 more)

### Community 44 - "handleManualEditActivity"
Cohesion: 0.16
Nodes (26): clearStoredManualApplyState(), fetchPendingCount(), handleManualEditActivity(), hasTextRows(), hidePendingApplyDock(), manualApplyLoadingText(), manualApplyStateKey(), manualEditEventForCurrentPage() (+18 more)

### Community 45 - "voice_companion.py"
Cohesion: 0.13
Nodes (26): can_access_patient(), No-implicit-access: staff may view any patient; owners and linked family…, chat_text(), chat_voice(), _companion_error(), ConfigCreateRequest, ConfigResponse, create_voice_config() (+18 more)

### Community 46 - "test_language_service.py"
Cohesion: 0.16
Nodes (21): get_language_service(), MockLanguageService, Deterministic local language provider for testing and offline development., Dependency injector for speech and language service. `provider` overrides…, _client(), asyncio, MockTransport, Phase 8 tests — Bhashini provider & factory selection. (+13 more)

### Community 47 - "BaselineData"
Cohesion: 0.14
Nodes (9): BaselineData, PatientReportData, _apply_report_adjustments(), _clamp_difficulty(), _compute_baseline_composite(), determine_starting_difficulty(), _rt_factor(), _score_to_difficulty() (+1 more)

### Community 48 - "captureElementToBlob"
Cohesion: 0.11
Nodes (23): averageRgb01(), captureAndEmit(), captureChromeNodes(), captureElementFromRenderedAncestor(), captureElementToBlob(), checkpointPayload(), compileShader(), cssColorToRgb01() (+15 more)

### Community 49 - "offline_sync_service.dart"
Cohesion: 0.08
Nodes (23): @DriftDatabase, ../config/app_config.dart, dart:async, ../database/app_database.dart, AppDatabase, api, db, enqueueGameSession (+15 more)

### Community 50 - "auth_session.dart"
Cohesion: 0.08
Nodes (23): AuthStatus get, bool get, ChangeNotifier, dart:convert, UserModel, _applyTokens, AuthSession, AuthStatus (+15 more)

### Community 51 - "reminders.py"
Cohesion: 0.18
Nodes (23): ensure_patient_access(), Resolve a patient profile and enforce no-implicit-access. 404 when the patient…, acknowledge_event(), AcknowledgeEventRequest, Config, create_schedule(), CreateScheduleRequest, deactivate_schedule() (+15 more)

### Community 52 - "AuthService"
Cohesion: 0.17
Nodes (18): Single-use rotation: only the current jti is accepted; a new pair revokes the…, refresh_token(), AuthService, Create a JWT access token., Create a single-use refresh token. Returns (token, jti). The jti is stored on…, Verify and decode a JWT token., create_access_token(), create_refresh_token() (+10 more)

### Community 53 - "test_phase12_gates.py"
Cohesion: 0.17
Nodes (17): Config, Refuse to boot a production process with placeholder secrets or open CORS., Settings, _login(), _patient(), asyncio, Consent-scope, permission-tier, export, and production-boot gates., _register() (+9 more)

### Community 54 - "ConversationStore"
Cohesion: 0.15
Nodes (14): ConversationStore, _demo(), Per-patient conversation history for the voice companion. Seam: Redis when…, Turn-taking memory keyed by patient id., reset_conversation_store_for_tests(), load_persona_prompt(), _patient_with_consent(), asyncio (+6 more)

### Community 55 - "auth.py"
Cohesion: 0.17
Nodes (19): login(), logout(), AsyncSession, BaseModel, Auth routes — register, login, refresh, logout, me., Revoke the current refresh token (JWT access stays stateless)., RefreshRequest, register() (+11 more)

### Community 56 - "AdaptiveEngine"
Cohesion: 0.23
Nodes (11): AdaptiveEngine, Any, example_1_baseline_only(), example_2_baseline_with_report(), example_3_severe_cases(), example_4_adaptive_over_sessions(), example_5_decline_scenario(), example_6_patient_history_and_summary() (+3 more)

### Community 57 - "test_retention_service.py"
Cohesion: 0.24
Nodes (18): maintenance_once(), Consume the sync outbox and run retention in one maintenance pass., DocumentChunk, MedicalDocument, SymptomLog, AsyncSession, datetime, Data-retention & deletion maintenance (DPDP Act 2023, Phase 11). Applies the… (+10 more)

### Community 58 - "ApiService"
Cohesion: 0.14
Nodes (21): _DashboardScreen, _DashboardScreenState, _LoginScreen, _LoginScreenState, _Root, _RootState, AuthScreen, _AuthScreenState (+13 more)

### Community 59 - "models.py"
Cohesion: 0.25
Nodes (15): _apply_decision(), _avg(), _baseline_strength_factor(), _classify_trend(), decide_next_difficulty(), _linear_trend(), _make_reason(), CognitiveStatus (+7 more)

### Community 60 - "AppDelegate"
Cohesion: 0.11
Nodes (14): Flutter, FlutterAppDelegate, FlutterImplicitEngineBridge, FlutterImplicitEngineDelegate, FlutterSceneDelegate, AppDelegate, Any, Bool (+6 more)

### Community 61 - "resolveLiveInjectionAnchor"
Cohesion: 0.16
Nodes (19): buildSvelteExpressionTextMap(), buildSveltePropValuesFromLiveElement(), buildSveltePropValuesV2(), cloneWithoutElements(), collectTextNodes(), collectVisibleTexts(), cssEscapeIdent(), elementMatchesOriginalMarkup() (+11 more)

### Community 62 - "pack_picker_screen.dart"
Cohesion: 0.11
Nodes (18): ../data/local_content_packs.dart, match_it_screen.dart, MaterialPageRoute, build, _api, build, createState, _difficulty (+10 more)

### Community 63 - "createLiveBrowserSessionState"
Cohesion: 0.21
Nodes (15): createLiveBrowserSessionState(), clearHandled(), clearScrollY(), clearSession(), isHandled(), loadSession(), markHandled(), nextCheckpointRevision() (+7 more)

### Community 64 - "generate_match_it_board"
Cohesion: 0.14
Nodes (17): ContentItem, ContentPack, generate_match_it_board(), list_content_packs(), Any, NER-Themed Content Packs & Match-It Board Generator. Seedable content packs…, Register (or replace) a themed set so caregivers/admins can add packs without a…, Return summary metadata for all registered content packs. (+9 more)

### Community 65 - "onAnnotDown"
Cohesion: 0.20
Nodes (17): beginEditPin(), buildAnnotationsForCapture(), buildPinElement(), cancelEditingPin(), clampPlaceholderSize(), finalizeEditingPin(), initAnnotOverlay(), localCoords() (+9 more)

### Community 66 - "dashboard.py"
Cohesion: 0.18
Nodes (14): acknowledge_alert(), get_caregiver_patients(), get_patient_summary(), AsyncSession, UUID, Caregiver & Clinician Dashboard API Routes., Retrieve all patients linked to this caregiver / ASHA worker., Retrieve 7-day cognitive trends, reminder compliance, and active alerts for a… (+6 more)

### Community 67 - "PerformanceTracker"
Cohesion: 0.16
Nodes (4): GamePerformance, _make_key(), PerformanceTracker, HistoryKey

### Community 68 - "createLiveBrowserDomHelpers"
Cohesion: 0.17
Nodes (10): createLiveBrowserDomHelpers(), cssId(), liveUiRoot(), makeFrozenAnchor(), own(), pickable(), rectIsUsableAnchor(), uiAppend() (+2 more)

### Community 69 - "reminder_scheduler.dart"
Cohesion: 0.12
Nodes (15): FlutterLocalNotificationsPlugin, cancelAll, cancelSchedule, initialize, _initialized, instance, _nextInstanceOf, _parseTimes (+7 more)

### Community 70 - "LanguageServiceError"
Cohesion: 0.28
Nodes (7): BhashiniLanguageService, LanguageServiceError, AsyncBaseTransport, Exception, Walk nested ULCA response (dicts + list indexes); None if missing., Raised when a language provider cannot complete a request., Real Government of India Bhashini (ULCA) inference pipeline client.

### Community 71 - "deps.py"
Cohesion: 0.21
Nodes (10): Security dependency helpers., Build a FastAPI dependency that enforces role-based access. Usage:…, require_role(), verify_token(), get_current_user(), _parse_sub(), Auth + patient-access dependencies. - get_current_user: extracts the user from…, JWT 'sub' is a stringified UUID; normalize for UUID column comparison. (+2 more)

### Community 72 - "test_api_routes.py"
Cohesion: 0.35
Nodes (12): _create_patient(), _login(), asyncio, API route tests — auth refresh, patient profiles + caregiver links, sync, games…, Phase 8-10 endpoints are mounted and auth-gated where required., Regression: games routes previously crashed with TypeError from require_role…, _register(), test_auth_refresh_flow() (+4 more)

### Community 74 - "DataClass"
Cohesion: 0.26
Nodes (13): Insertable, UpdateCompanion, DataClass, GameActionRow, GameActionsCompanion, GameSessionRow, GameSessionsCompanion, PatientRoutineRow (+5 more)

### Community 75 - "get_db"
Cohesion: 0.20
Nodes (10): AsyncClient, get_db(), AsyncSession, Dependency for FastAPI routes: provides async DB session., Database module alias., client(), db_session(), AsyncSession (+2 more)

### Community 77 - "scheduleAcceptCleanup"
Cohesion: 0.31
Nodes (11): acceptedDomAlreadyClean(), clearHandledWrapperReloadStamp(), deferredRecoverySuperseded(), ensureAcceptedDomClean(), findAcceptedRuntimeWrappers(), handledWrapperReloadKey(), reloadAfterMissingAcceptedDom(), restoreAcceptedDomFromSnapshot() (+3 more)

### Community 78 - "models/shared_models.dart"
Cohesion: 0.18
Nodes (10): api_service.dart, OfflineSyncService, acknowledgeReminder, apiService, getSchedules, getTodaysEvents, MobileReminderService, sync (+2 more)

### Community 79 - "main.py"
Cohesion: 0.22
Nodes (10): _env_int(), Launch the periodic loop as a task on the running event loop (API lifespan)., start_in_background(), health_check(), lifespan(), Serve single-page application UI at root URL., Health check endpoint for load balancers., root() (+2 more)

### Community 80 - "RateLimitMiddleware"
Cohesion: 0.24
Nodes (5): RateLimitMiddleware, IP rate limiting — 100 req/min default (Phase 12). Uses Redis when reachable so…, BaseHTTPMiddleware, Request, Response

### Community 81 - ".hash_password"
Cohesion: 0.22
Nodes (9): Hash a password using bcrypt directly., Verify a plain password against a hashed one., Verify password hashing and JWT encoding/decoding., test_auth_and_tokens(), hash_password(), verify_password(), t_pw_hash(), _get_or_create_user() (+1 more)

### Community 82 - "dashboard/web/manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, prefer_related_applications, short_name (+2 more)

### Community 83 - "mobile/web/manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, prefer_related_applications, short_name (+2 more)

### Community 84 - "local_content_packs.dart"
Cohesion: 0.20
Nodes (9): dart:math, board, defaultRoutineBoard, LocalContentPacks, _rng, summaries, ../models/game_models.dart, static const List (+1 more)

### Community 85 - "extract_document_text"
Cohesion: 0.33
Nodes (8): _decode_text(), extract_document_text(), _extract_pdf(), _looks_like_pdf(), _looks_like_text(), Document text extraction for RAG ingestion (PDF / plain text / markdown).…, Extract plaintext from an uploaded document's bytes. PDF via pypdf (pure…, Heuristic: decode-able as UTF-8 and mostly printable characters.

### Community 87 - "test_document_upload.py"
Cohesion: 0.50
Nodes (7): _clinician_with_patient(), asyncio, P5 — document file upload: PDF/text extraction feeds the existing RAG ingest.…, test_upload_real_pdf(), test_upload_rejects_empty_file(), test_upload_rejects_unsupported_type(), test_upload_text_file_ingests_and_answers()

### Community 88 - "test_phase5_game_stats.py"
Cohesion: 0.43
Nodes (7): _clinician_patient(), asyncio, P5 — GET /games/patients/{id}/stats: accuracy + response-time trends., A basic-tier family caregiver is blocked from raw stats (dashboard already…, test_stats_empty_window(), test_stats_requires_clinical_tier(), test_stats_trend_and_deltas()

### Community 89 - "live-browser-ignores.js"
Cohesion: 0.52
Nodes (6): globToRegex(), matchesScope(), normalizeIgnoreRule(), normalizeIgnoreValue(), pageCandidates(), resolveDetectIgnores()

### Community 90 - "@DataClassName"
Cohesion: 0.48
Nodes (7): @DataClassName, GameActions, GameSessions, PatientRoutines, ReminderEvents, SyncQueue, Table

### Community 91 - "dev_role_menu.dart"
Cohesion: 0.29
Nodes (6): _accounts, build, DevRoleMenu, enabled, services/auth_session.dart, static const

### Community 92 - "impeccable"
Cohesion: 0.70
Nodes (4): impeccable script, check_download(), fetch_url(), probe_ok()

### Community 93 - "smoke_e2e.py"
Cohesion: 0.50
Nodes (4): check(), main(), End-to-end API smoke test against a live backend + real database. Usage:…, Assert an HTTP response; print FAIL (with detail) and return parsed body.

### Community 94 - "app_config.dart"
Cohesion: 0.40
Nodes (4): apiV1, AppConfig, _defined, package:flutter/foundation.dart

### Community 95 - "game_labels.dart"
Cohesion: 0.40
Nodes (4): fallbackLanguage, GameLabels, of, static const String

### Community 97 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

## Knowledge Gaps
- **893 isolated node(s):** `Config`, `clearSyncedItems`, `acknowledgedAt`, `actionData`, `actionType` (+888 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1413 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_post` connect `User` to `sync.py`, `patients.py`, `dashboard.py`, `language.py`, `reports.py`, `dashboard/lib/main.dart`, `voice_companion.py`, `reminders.py`, `AuthService`, `auth.py`, `games.py`, `VoiceCompanionService`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `_get` connect `User` to `sync.py`, `patients.py`, `dashboard.py`, `language.py`, `reports.py`, `dashboard/lib/main.dart`, `main.py`, `ReportService`, `reminders.py`, `games.py`, `VoiceCompanionService`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `all_models.py`, `ReminderEvent`, `ReportService`, `notification_service.py`, `jobs.py`, `games.py`, `VoiceCompanionService`, `sync.py`, `patients.py`, `language.py`, `reports.py`, `voice_companion.py`, `reminders.py`, `AuthService`, `auth.py`, `test_retention_service.py`, `dashboard.py`, `deps.py`, `.hash_password`, `test_phase5_game_stats.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `User` (e.g. with `can_access_patient()` and `ensure_clinical_access()`) actually correct?**
  _`User` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `PatientProfile` (e.g. with `can_access_patient()` and `ensure_clinical_access()`) actually correct?**
  _`PatientProfile` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `GameSession` (e.g. with `_ensure_owned_session()` and `get_patient_stats()`) actually correct?**
  _`GameSession` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ReminderEvent` (e.g. with `escalation_scan()` and `acknowledge_event()`) actually correct?**
  _`ReminderEvent` has 16 INFERRED edges - model-reasoned connections that need verification._