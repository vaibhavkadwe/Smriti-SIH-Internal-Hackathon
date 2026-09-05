# Graph Report - SIH 26  (2026-09-05)

## Corpus Check
- 138 files · ~131,093 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1843 nodes · 3941 edges · 88 communities (72 shown, 10 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 469 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Drift DB (generated)
- Game Models (mobile)
- Auth Service & Schemas
- Sync Queue & Retention
- Shared Models (mobile)
- Games API
- Dashboard App (web)
- Mobile API Client
- Embedding Provider
- App Shells & Routing
- Project Docs & Decisions
- Data Models (backend)
- Reminders API
- Language Service
- LLM Client
- RAG Service
- Compliance & Dashboard Data
- Voice Companion Service
- Backend Core & Config
- Voice Companion API
- Encryption & Reports
- Match-It Game Logic
- Patients & Caregiver Links
- Match-It Screen
- Compliance Service
- Routine Game Logic
- Mobile Auth Session
- Notifications & Roles
- Reminder Engine
- Difficulty Rules Tests
- Caregiver Dashboard Screen
- Routine Screen
- Phase 12 Hardening Tests
- Dashboard & Sync API
- Notification Service
- Reminders Screen
- Offline Sync Service
- Language Service Tests
- Voice Companion Screen
- Game Board Generators
- iOS Runner Host
- Difficulty Engine
- Game Session Service
- Login & Dashboard Widgets
- Mobile Reminder Service
- Local Notification Scheduler
- Background Jobs
- Escalation & Audit Jobs
- Consent & Audit API
- Medical Docs API
- Bhashini Provider
- Routine Service (backend)
- Patient Access Control
- API Route Tests
- Trend Chart Widget
- Content Pack Picker
- Drift Row Companions
- Content Packs Service
- Rate Limit Middleware
- Game Engine & Adaptivity
- Local Content Packs
- Dashboard Web Manifest
- Mobile Web Manifest
- Deployment Stack
- Voice Pipeline Internals
- Flutter Widget Tests
- Drift Table Definitions
- Test Fixtures
- E2E Smoke Test
- Initial DB Migration
- Cadence Parser
- Drift Database Class
- DPDP Compliance Plan
- Android Host
- Backend Package Init
- Commit Script
- Auth Design Notes
- Language Provider Design
- Setup Script
- Nullable Bool Type
- DateTime Type
- Exception Type

## God Nodes (most connected - your core abstractions)
1. `User` - 93 edges
2. `PatientProfile` - 48 edges
3. `GameSession` - 38 edges
4. `ReminderEvent` - 38 edges
5. `ReminderService` - 38 edges
6. `ComplianceService` - 36 edges
7. `LLMClient` - 35 edges
8. `RAGService` - 35 edges
9. `GameTypeEnum` - 34 edges
10. `VoiceCompanionService` - 34 edges

## Surprising Connections (you probably didn't know these)
- `Offline-First Gaming (Deep Sync Queue)` --semantically_similar_to--> `Offline-First Gaming + Sync Queue Architecture`  [INFERRED] [semantically similar]
  brainstorm-demo-features.html → CLAUDE.md
- `Voice Companion in Regional Languages` --semantically_similar_to--> `Voice Companion (Bhashini + Claude)`  [INFERRED] [semantically similar]
  brainstorm-demo-features.html → CLAUDE.md
- `Caregiver Mobile App (Lite)` --semantically_similar_to--> `Caregiver Dashboard on Flutter Web (shared models)`  [INFERRED] [semantically similar]
  brainstorm-demo-features.html → CLAUDE.md
- `Caregiver Dashboard (eldercare_dashboard, Flutter Web app)` --semantically_similar_to--> `Caregiver Dashboard on Flutter Web (shared models)`  [INFERRED] [semantically similar]
  dashboard/README.md → CLAUDE.md
- `AI-Powered Alert Engine (rule-based + LLM triage)` --semantically_similar_to--> `Reminder Escalation Thresholds`  [INFERRED] [semantically similar]
  brainstorm-demo-features.html → CLAUDE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Offline-first gaming architecture (brainstorm → decision → games engine)** — brainstorm_demo_features_offline_first, claude_offline_first_sync, phase2_summary_games_engine [INFERRED 0.85]
- **Claude + Bhashini AI language layer (voice companion, multilingual, RAG share the LLM stack)** — claude_voice_companion, claude_multilingual_scope, phase_1_status_rag_pipeline [INFERRED 0.80]
- **Cognitive games engine composed of games, content, difficulty and logging** — phase2_summary_games_engine, phase2_summary_match_it, phase2_summary_routine_sequencing, phase2_summary_adaptive_difficulty, phase2_summary_ner_content_packs, phase2_summary_game_session_logging [INFERRED 0.85]
- **Offline-first sync architecture (design -> impl -> consumer)** — docs_superpowers_plans_2026_09_04_phase1_scaffold_data_models_offline_first_sync, mobile_lib_database_readme_offline_sync_layer, docs_superpowers_plans_2026_09_05_remaining_roadmap_to_mvp_sync_queue_consumer [INFERRED 0.80]
- **Local dev stack (docker-compose: db + redis + backend)** — docker_compose_db, docker_compose_redis, docker_compose_backend [EXTRACTED 0.90]
- **Phase 11 DPDP compliance pass components** — docs_superpowers_plans_2026_09_05_remaining_roadmap_to_mvp_phase11_compliance_pass, docs_superpowers_plans_2026_09_05_remaining_roadmap_to_mvp_access_control_gaps, docs_superpowers_plans_2026_09_05_remaining_roadmap_to_mvp_sync_queue_consumer, docs_superpowers_plans_2026_09_05_remaining_roadmap_to_mvp_column_encryption [EXTRACTED 0.90]

## Communities (88 total, 10 thin omitted)

### Community 0 - "Drift DB (generated)"
Cohesion: 0.01
Nodes (158): BoolColumn get, class PatientRoutineRow extends, class ReminderEventRow extends, ColumnFilters, ColumnOrderings, dart:io, DateTimeColumn get, GeneratedColumn (+150 more)

### Community 1 - "Game Models (mobile)"
Cohesion: 0.03
Nodes (76): accuracyPct, actionData, actionType, avgResponseTimeMs, cardId, cards, completedAt, copyWith (+68 more)

### Community 2 - "Auth Service & Schemas"
Cohesion: 0.07
Nodes (49): verify_token(), get_current_user(), _parse_sub(), JWT 'sub' is a stringified UUID; normalize for UUID column comparison., Auth middleware exports., login(), AsyncSession, BaseModel (+41 more)

### Community 3 - "Sync Queue & Retention"
Cohesion: 0.09
Nodes (53): DocumentChunk, MedicalDocument, Base, SymptomLog, SyncOperationEnum, SyncQueue, SyncResourceTypeEnum, AsyncSession (+45 more)

### Community 4 - "Shared Models (mobile)"
Cohesion: 0.04
Nodes (54): double?, acknowledgedAt, acknowledgmentMethod, attempts, avgResponseTimeMs, baselineFromApi, baselineToApi, cadence (+46 more)

### Community 5 - "Games API"
Cohesion: 0.07
Nodes (48): complete_game(), ContentItemIn, ContentPackCreate, ContentPackSummary, create_content_pack(), DifficultyEvaluationResponse, _ensure_owned_session(), evaluate_difficulty() (+40 more)

### Community 6 - "Dashboard App (web)"
Cohesion: 0.04
Nodes (48): _ack, acknowledge, _Api, _baseUrl, build, _buildBody, _busy, caregiverId (+40 more)

### Community 7 - "Mobile API Client"
Cohesion: 0.04
Nodes (46): dart:developer, int?, accessToken, acknowledgeAlert, acknowledgeReminder, ApiException, authToken, AuthTokens (+38 more)

### Community 8 - "Embedding Provider"
Cohesion: 0.09
Nodes (29): _build_provider(), EmbeddingProvider, EmbeddingUnavailableError, get_embedding_provider(), HeuristicEmbeddingProvider, LocalSentenceTransformerProvider, OpenAIEmbeddingProvider, ABC (+21 more)

### Community 9 - "App Shells & Routing"
Cohesion: 0.06
Nodes (36): CaregiverDashboardApp, FormState, MaterialPageRoute, _api, _AuthGate, build, _busy, _create (+28 more)

### Community 10 - "Project Docs & Decisions"
Cohesion: 0.14
Nodes (35): CI Backend Job (tests + live PG smoke), CI Frontend Job (Flutter analyze + drift codegen), Backend Python Dependencies, AI-Powered Alert Engine (rule-based + LLM triage), Caregiver Mobile App (Lite), Demo-Worthy Features Brainstorm, Achievement & Streak System, Offline-First Gaming (Deep Sync Queue) (+27 more)

### Community 11 - "Data Models (backend)"
Cohesion: 0.14
Nodes (28): Alembic environment configuration for Elder-Care platform., Run migrations in 'offline' mode — emits SQL to stdout., Run migrations against a live database., run_migrations_offline(), run_migrations_online(), DocumentTypeEnum, EmbeddingStatusEnum, Enum (+20 more)

### Community 12 - "Reminders API"
Cohesion: 0.15
Nodes (25): AcknowledgmentMethodEnum, acknowledge_event(), AcknowledgeEventRequest, Config, create_schedule(), CreateScheduleRequest, deactivate_schedule(), evaluate_escalations() (+17 more)

### Community 13 - "Language Service"
Cohesion: 0.09
Nodes (25): ASRRequest, _get_provider(), _handle(), language_status(), BaseModel, HTTPException, Speech & Language Translation API Routes. Routes wrap the configured language…, Translate between NER regional languages and English. (+17 more)

### Community 14 - "LLM Client"
Cohesion: 0.11
Nodes (25): detect_provider(), LLMClient, LLMServiceError, AsyncBaseTransport, Exception, Drop paid slugs when free-only mode is on (OpenRouter only)., Return (url, headers, payload) for the active provider., Extract reply text, or '' when the model returned no usable content. (+17 more)

### Community 15 - "RAG Service"
Cohesion: 0.16
Nodes (22): Any, AsyncSession, UUID, RAGService, Store a medical document and index chunk embeddings for RAG search.…, Retrieve the most relevant chunks for a patient's clinical query., Answer a clinical question grounded in the patient's documents. Uses Claude…, Embed via the configured provider (heuristic default; local/openai optional). (+14 more)

### Community 16 - "Compliance & Dashboard Data"
Cohesion: 0.12
Nodes (23): AlertFlag, CognitiveBaselineEnum, PatientProfile, Caregiver & Clinician Dashboard API Routes., Digital Personal Data Protection (DPDP) Act 2023 & Encryption Service.…, DashboardService, Any, AsyncSession (+15 more)

### Community 17 - "Voice Companion Service"
Cohesion: 0.17
Nodes (21): VoiceCompanionConfig, MockLanguageService, Deterministic local language provider for testing and offline development., AsyncSession, Return the active system prompt, seeding the default row when empty., Fetch the active voice companion config, seeding defaults if none exist., VoiceCompanionService, asyncio (+13 more)

### Community 18 - "Backend Core & Config"
Cohesion: 0.13
Nodes (17): Security dependency helpers., Build a FastAPI dependency that enforces role-based access. Usage:…, require_role(), get_db(), AsyncSession, Dependency for FastAPI routes: provides async DB session., Database module alias., Auth + patient-access dependencies. - get_current_user: extracts the user from… (+9 more)

### Community 19 - "Voice Companion API"
Cohesion: 0.14
Nodes (26): logout(), Log out. JWT is stateless, so the client discards its tokens., activate_voice_config(), chat_text(), chat_voice(), _companion_error(), ConfigCreateRequest, ConfigResponse (+18 more)

### Community 20 - "Encryption & Reports"
Cohesion: 0.14
Nodes (22): EncryptionService, AES-256 Fernet-based field level encryption., Encrypt sensitive clinical text., Decrypt ciphertext back to plaintext., Any, AsyncSession, UUID, Automated Clinical & Cognitive Report Generation Service. Aggregates: - Game… (+14 more)

### Community 21 - "Match-It Game Logic"
Cohesion: 0.07
Nodes (27): MatchItBoard, accuracyPct, attempts, board, cards, copyWith, correctMatches, flippedCards (+19 more)

### Community 22 - "Patients & Caregiver Links"
Cohesion: 0.15
Nodes (26): CaregiverPatientLink, PermissionTierEnum, RelationshipTypeEnum, _baseline(), _can_view_patient(), CaregiverLinkRequest, CaregiverLinkResponse, create_patient() (+18 more)

### Community 23 - "Match-It Screen"
Cohesion: 0.07
Nodes (26): MatchItCard, _api, build, card, _completeAndShowResults, createState, difficultyLevel, dispose (+18 more)

### Community 24 - "Compliance Service"
Cohesion: 0.15
Nodes (20): ensure_consent(), Purpose-limitation gate: 403 unless an active ConsentRecord covers the scope., export_patient_data(), DPDP right of access — JSON dump of the patient's stored records., get_patient_history(), Retrieve game history for a patient (clinical-tier view). Audited., get_weekly_clinical_report(), Generate structured weekly cognitive and clinical evaluation report. (+12 more)

### Community 25 - "Routine Game Logic"
Cohesion: 0.08
Nodes (25): double get, int get, RoutineBoard, accuracyPct, board, canPlaceMore, copyWith, correctPlacements (+17 more)

### Community 26 - "Mobile Auth Session"
Cohesion: 0.08
Nodes (24): AuthStatus get, bool get, ChangeNotifier, dart:convert, UserModel, _applyTokens, AuthSession, AuthStatus (+16 more)

### Community 27 - "Notifications & Roles"
Cohesion: 0.16
Nodes (18): AlertSeverityEnum, AlertTriggerTypeEnum, Enum, str, RoleEnum, ConsoleNotificationProvider, Local mock transport: logs each delivery and appends to ``deliveries``.…, datetime (+10 more)

### Community 28 - "Reminder Engine"
Cohesion: 0.21
Nodes (20): ReminderEvent, ReminderSchedule, ReminderTypeEnum, Any, Escalation Rules: 1. 10 minutes unacknowledged -> Escalate to secondary…, Materialize a PENDING ReminderEvent for each active schedule's due times that…, Test reminder acknowledgment and multi-day alert escalation., test_reminder_escalation_rules() (+12 more)

### Community 29 - "Difficulty Rules Tests"
Cohesion: 0.10
Nodes (12): Drop difficulty if 2+ consecutive sessions both have <50% accuracy., Rule-based difficulty adjustment using explicit thresholds., Bump difficulty if 3+ consecutive sessions all have >85% accuracy., RuleBasedDifficultyStrategy, t_bump_rule_high_accuracy(), t_difficulty_strategy_interface(), t_drop_rule_low_accuracy(), t_bump_rule() (+4 more)

### Community 30 - "Caregiver Dashboard Screen"
Cohesion: 0.09
Nodes (23): _acknowledge, _adherence, _alerts, _api, build, _buildBody, CaregiverDashboardScreen, _CaregiverDashboardScreenState (+15 more)

### Community 31 - "Routine Screen"
Cohesion: 0.09
Nodes (23): _api, build, createState, difficultyLevel, _error, _game, _iconFor, initState (+15 more)

### Community 32 - "Phase 12 Hardening Tests"
Cohesion: 0.17
Nodes (17): Config, Refuse to boot a production process with placeholder secrets or open CORS., Settings, _login(), _patient(), asyncio, Consent-scope, permission-tier, export, and production-boot gates., _register() (+9 more)

### Community 33 - "Dashboard & Sync API"
Cohesion: 0.12
Nodes (22): health_check(), Health check endpoint for load balancers., Base, User, me(), acknowledge_alert(), get_caregiver_patients(), get_patient_summary() (+14 more)

### Community 34 - "Notification Service"
Cohesion: 0.15
Nodes (20): _build_provider(), get_notification_provider(), LogOnlyFallbackProvider, NotificationError, NotificationProvider, notify_escalation_results(), notify_reprompts(), ABC (+12 more)

### Community 35 - "Reminders Screen"
Cohesion: 0.09
Nodes (22): Map, build, _colorFor, createState, _error, _handleAcknowledge, _iconFor, initState (+14 more)

### Community 36 - "Offline Sync Service"
Cohesion: 0.09
Nodes (21): ../config/app_config.dart, dart:async, ../database/app_database.dart, api, db, enqueueGameSession, enqueueReminderAck, enqueueStoredUnsynced (+13 more)

### Community 37 - "Language Service Tests"
Cohesion: 0.20
Nodes (19): get_language_service(), Dependency injector for speech and language service. `provider` overrides…, _client(), asyncio, MockTransport, Phase 8 tests — Bhashini provider & factory selection., test_asr_payload_and_parse(), test_factory_auto_returns_mock_without_credentials() (+11 more)

### Community 38 - "Voice Companion Screen"
Cohesion: 0.10
Nodes (20): _api, build, _companionCard, createState, dispose, _history, _inputBar, _languages (+12 more)

### Community 39 - "Game Board Generators"
Cohesion: 0.13
Nodes (16): generate_match_it_board(), Generate a randomized match-it board configuration for a given pack and…, generate_routine_sequencing_board(), Generate a routine sequencing puzzle with shuffled steps according to…, Self-contained test runner that doesn't depend on pytest being installed., t_game(), t_generate_board_easy(), t_generate_board_hard() (+8 more)

### Community 40 - "iOS Runner Host"
Cohesion: 0.11
Nodes (14): Flutter, FlutterAppDelegate, FlutterImplicitEngineBridge, FlutterImplicitEngineDelegate, FlutterSceneDelegate, AppDelegate, Any, Bool (+6 more)

### Community 41 - "Difficulty Engine"
Cohesion: 0.18
Nodes (16): DifficultyAdjustmentLog, DifficultyStrategy, evaluate_difficulty(), get_recent_sessions(), _log_adjustment(), ABC, Any, AsyncSession (+8 more)

### Community 42 - "Game Session Service"
Cohesion: 0.25
Nodes (16): GameSession, Game Engine Service — Unified Class Interface for Game Sessions & Adaptive…, complete_game_session(), get_patient_game_history(), get_session_summary(), Any, AsyncSession, UUID (+8 more)

### Community 43 - "Login & Dashboard Widgets"
Cohesion: 0.16
Nodes (18): _DashboardScreen, _DashboardScreenState, _LoginScreen, _LoginScreenState, _Root, _RootState, AuthScreen, _AuthScreenState (+10 more)

### Community 44 - "Mobile Reminder Service"
Cohesion: 0.12
Nodes (15): api_service.dart, apiV1, AppConfig, _defined, ApiService, OfflineSyncService, acknowledgeReminder, apiService (+7 more)

### Community 45 - "Local Notification Scheduler"
Cohesion: 0.12
Nodes (15): FlutterLocalNotificationsPlugin, cancelAll, cancelSchedule, initialize, _initialized, instance, _nextInstanceOf, _parseTimes (+7 more)

### Community 46 - "Background Jobs"
Cohesion: 0.22
Nodes (14): _env_int(), generate_events(), main(), maintenance_once(), _periodic_loop(), AsyncSession, Background jobs — reminder escalation, sync consumption, retention. Implements…, Run each job on its own cadence; failures never abort the loop. (+6 more)

### Community 47 - "Escalation & Audit Jobs"
Cohesion: 0.28
Nodes (14): escalation_scan(), Escalate unacknowledged reminders, send reprompts, mark misses, raise alerts.…, ReminderStatusEnum, asyncio, Tests for background jobs (escalation scan) + admin audit-log endpoint., Only admins may list the audit trail; rows are returned newest-first., Patient with an unacknowledged reminder older than 10 minutes., 3 unresolved reminders of one type in 7 days -> AlertFlag + notification. (+6 more)

### Community 48 - "Consent & Audit API"
Cohesion: 0.22
Nodes (14): ConsentCreateRequest, ConsentResponse, grant_consent(), list_audit_logs(), list_patient_consents(), AsyncSession, BaseModel, UUID (+6 more)

### Community 49 - "Medical Docs API"
Cohesion: 0.15
Nodes (15): answer_medical_question(), DocumentAnswerRequest, DocumentQueryRequest, DocumentUploadRequest, ingest_medical_document(), AsyncSession, BaseModel, UUID (+7 more)

### Community 50 - "Bhashini Provider"
Cohesion: 0.28
Nodes (7): BhashiniLanguageService, LanguageServiceError, AsyncBaseTransport, Exception, Walk nested ULCA response (dicts + list indexes); None if missing., Raised when a language provider cannot complete a request., Real Government of India Bhashini (ULCA) inference pipeline client.

### Community 51 - "Routine Service (backend)"
Cohesion: 0.18
Nodes (14): get_patient_routine(), Any, AsyncSession, UUID, Daily Routine Sequencing Game Service & Caregiver Routine Editor. Enables…, Retrieve custom routine for patient, or fallback to default., Caregiver routine editor: save custom steps to PatientProfile.routine., Validate submitted sequence against target. Computes correctness,… (+6 more)

### Community 52 - "Patient Access Control"
Cohesion: 0.24
Nodes (13): can_access_patient(), ensure_clinical_access(), ensure_patient_access(), get_permission_tier(), load_patient(), AsyncSession, UUID, Resolve basic | clinical for this caller against this patient. (+5 more)

### Community 53 - "API Route Tests"
Cohesion: 0.35
Nodes (12): _create_patient(), _login(), asyncio, API route tests — auth refresh, patient profiles + caregiver links, sync, games…, Phase 8-10 endpoints are mounted and auth-gated where required., Regression: games routes previously crashed with TypeError from require_role…, _register(), test_auth_refresh_flow() (+4 more)

### Community 54 - "Trend Chart Widget"
Cohesion: 0.15
Nodes (12): Color, CustomPainter, List, build, color, paint, shouldRepaint, _SparklinePainter (+4 more)

### Community 55 - "Content Pack Picker"
Cohesion: 0.15
Nodes (12): ../data/local_content_packs.dart, match_it_screen.dart, _api, build, createState, _difficulty, _error, initState (+4 more)

### Community 56 - "Drift Row Companions"
Cohesion: 0.26
Nodes (13): Insertable, UpdateCompanion, DataClass, GameActionRow, GameActionsCompanion, GameSessionRow, GameSessionsCompanion, PatientRoutineRow (+5 more)

### Community 57 - "Content Packs Service"
Cohesion: 0.21
Nodes (11): ContentItem, ContentPack, list_content_packs(), Any, NER-Themed Content Packs & Match-It Board Generator. Seedable content packs…, Register (or replace) a themed set so caregivers/admins can add packs without a…, Return summary metadata for all registered content packs., register_content_pack() (+3 more)

### Community 58 - "Rate Limit Middleware"
Cohesion: 0.24
Nodes (5): RateLimitMiddleware, IP rate limiting — 100 req/min default (Phase 12). Uses Redis when reachable so…, BaseHTTPMiddleware, Request, Response

### Community 59 - "Game Engine & Adaptivity"
Cohesion: 0.31
Nodes (9): GameTypeEnum, GameEngineService, AsyncSession, UUID, Create and complete a game session with explicit outcome metrics., Compute the next adaptive difficulty level and reasoning., Test game session logging and rule-based difficulty adjustment., test_game_engine_and_adaptive_difficulty() (+1 more)

### Community 60 - "Local Content Packs"
Cohesion: 0.18
Nodes (10): dart:math, board, defaultRoutineBoard, LocalContentPacks, _rng, summaries, ../models/game_models.dart, ../models/shared_models.dart (+2 more)

### Community 61 - "Dashboard Web Manifest"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, prefer_related_applications, short_name (+2 more)

### Community 62 - "Mobile Web Manifest"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, prefer_related_applications, short_name (+2 more)

### Community 63 - "Deployment Stack"
Cohesion: 0.24
Nodes (10): eldercare_dashboard (Caregiver Web Dashboard package), backend service (FastAPI), db service (PostgreSQL + pgvector), redis service (cache/queue), Offline-First Sync Queue Architecture (Phase 1 design), Phase 12: Production Hardening, RAG pipeline (chunk -> embed -> pgvector -> Claude), Sync-queue consumer (outbox -> encrypted SymptomLog) (+2 more)

### Community 64 - "Voice Pipeline Internals"
Cohesion: 0.28
Nodes (6): CompanionServiceError, Any, Exception, Send a message to Claude; returns a dict with reply_text + metadata., Full Voice Pipeline: Bhashini ASR -> Claude -> Bhashini TTS. Each stage…, Raised when the companion cannot produce a reply (and fallback is disabled).

### Community 65 - "Flutter Widget Tests"
Cohesion: 0.22
Nodes (7): main, main, package:eldercare_dashboard/main.dart, package:eldercare_mobile/models/game_models.dart, package:eldercare_mobile/models/shared_models.dart, package:flutter_test/flutter_test.dart, package:shared_preferences/shared_preferences.dart

### Community 66 - "Drift Table Definitions"
Cohesion: 0.48
Nodes (7): @DataClassName, GameActions, GameSessions, PatientRoutines, ReminderEvents, SyncQueue, Table

### Community 67 - "Test Fixtures"
Cohesion: 0.50
Nodes (5): AsyncClient, client(), db_session(), AsyncSession, fixture

### Community 68 - "E2E Smoke Test"
Cohesion: 0.50
Nodes (4): check(), main(), End-to-end API smoke test against a live backend + real database. Usage:…, Assert an HTTP response; print FAIL (with detail) and return parsed body.

### Community 70 - "Cadence Parser"
Cohesion: 0.67
Nodes (3): Parse a cadence string into a sorted list of daily wall-clock times.…, test_parse_cadence_variants(), dtime

### Community 71 - "Drift Database Class"
Cohesion: 0.67
Nodes (3): _, @DriftDatabase, AppDatabase

### Community 72 - "DPDP Compliance Plan"
Cohesion: 0.67
Nodes (3): DPDP Compliance Foundation (ConsentRecord + AuditLog), Column-level AES-256 encryption at rest (unwired), Phase 11: DPDP Compliance Pass

## Knowledge Gaps
- **613 isolated node(s):** `Config`, `commit-phase1.sh script`, `_Api`, `_baseUrl`, `_token` (+608 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1006 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_post` connect `Voice Companion API` to `Dashboard & Sync API`, `Auth Service & Schemas`, `Games API`, `Dashboard App (web)`, `Reminders API`, `Language Service`, `Consent & Audit API`, `Medical Docs API`, `Patients & Caregiver Links`?**
  _High betweenness centrality (0.243) - this node is a cross-community bridge._
- **Why does `_get` connect `Dashboard & Sync API` to `Games API`, `Dashboard App (web)`, `Reminders API`, `Language Service`, `Consent & Audit API`, `Voice Companion API`, `Patients & Caregiver Links`, `Compliance Service`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Why does `User` connect `Dashboard & Sync API` to `Auth Service & Schemas`, `Notification Service`, `Sync Queue & Retention`, `Games API`, `Game Board Generators`, `Data Models (backend)`, `Reminders API`, `Language Service`, `Escalation & Audit Jobs`, `Consent & Audit API`, `Medical Docs API`, `Backend Core & Config`, `Voice Companion API`, `Patient Access Control`, `Patients & Caregiver Links`, `Compliance Service`, `Notifications & Roles`, `Reminder Engine`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `User` (e.g. with `can_access_patient()` and `ensure_clinical_access()`) actually correct?**
  _`User` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `PatientProfile` (e.g. with `can_access_patient()` and `ensure_clinical_access()`) actually correct?**
  _`PatientProfile` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `GameSession` (e.g. with `_ensure_owned_session()` and `ComplianceService`) actually correct?**
  _`GameSession` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `ReminderEvent` (e.g. with `escalation_scan()` and `acknowledge_event()`) actually correct?**
  _`ReminderEvent` has 15 INFERRED edges - model-reasoned connections that need verification._