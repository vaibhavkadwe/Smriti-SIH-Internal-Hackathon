# Graph Report - Smriti-SIH-Internal-Hackathon  (2026-09-06)

## Corpus Check
- 220 files · ~152,621 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3282 nodes · 5540 edges · 198 communities (177 shown, 14 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 504 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5cc36505`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app_database.dart
- game_models.dart
- AuthService
- ReportService
- shared_models.dart
- games.py
- dashboard/lib/main.dart
- api_service.dart
- dashboard/lib/theme/monad_theme.dart
- mobile/lib/main.dart
- Architecture & Decisions (CLAUDE.md)
- all_models.py
- mobile/lib/theme/monad_theme.dart
- Components
- LLMClient
- RAGService
- deps.py
- VoiceCompanionService
- sync.py
- game_analytics_engine.dart
- ConversationStore
- match_it_service.dart
- User
- match_it_screen.dart
- ComplianceService
- routine_service.dart
- auth_session.dart
- GSD Planner
- app.js
- test_phase2_services.py
- caregiver_dashboard_screen.dart
- routine_screen.dart
- test_phase12_gates.py
- GSD Roadmapper
- RoleEnum
- reminders_screen.dart
- offline_sync_service.dart
- language.py
- voice_companion_screen.dart
- test_language_service.py
- AppDelegate
- GameSession
- LanguageServiceError
- Verification Process
- GSD Integration Checker
- reminder_scheduler.dart
- jobs.py
- ensure_patient_access
- GSD Plan Checker
- _post
- test_phase6_7_alerts_reports.py
- database.py
- Architecture & Decisions — Elder-Care Cognitive Companion Platform
- test_api_routes.py
- dashboard/test/widget_test.dart
- pack_picker_screen.dart
- DataClass
- List
- RateLimitMiddleware
- GSD Project Researcher
- create_voice_config
- dashboard/web/manifest.json
- mobile/web/manifest.json
- backend service (FastAPI)
- reminders.py
- Remaining Roadmap to a Production-Ready MVP — SIH26003
- @DataClassName
- Get Shit Done (GSD) - Project Management System
- smoke_e2e.py
- 0001_initial_schema.py
- ReminderEvent
- AppDatabase
- DPDP Compliance Foundation (ConsentRecord + AuditLog)
- FlutterActivity
- app/__init__.py
- commit-phase1.sh
- JWT Auth + RBAC (Phase 1 design)
- Pluggable LanguageServiceProvider (Bhashini/Mock)
- setup.sh
- bool?
- DateTime
- Exception
- Codebase Design
- GSD Codebase Mapper
- GSD Phase Researcher
- 2026-09-04-phase1-scaffold-data-models.md
- Smriti — AI-Powered Cognitive Gaming and Memory Assistance Platform
- GSD Research Synthesizer
- HTML Report Format
- Shell Patterns for execute
- Process
- JavaScript / TypeScript Patterns for execute
- CI Frontend Job (Flutter analyze + drift codegen)
- Python Patterns for execute
- Offline-First Sync Queue Architecture (Phase 1 design)
- Deployment Guide — Elder-Care Cognitive Companion (SIH26003)
- Context Mode: Default for All Large Output
- Phase 1 Decisions
- Anti-Patterns: Common Mistakes with execute / execute_file
- Elder-Care Cognitive Companion Platform
- GSD Debugger
- Investigation Techniques
- Ponytail
- extract_document_text
- GSD Executor
- Summary Creation
- GSD Execute Phase
- test_document_upload.py
- dashboard_service.py
- Checkpoint Types
- Philosophy
- Verification Patterns
- Task Commit Protocol
- Checkpoint Protocol
- GSD Debug
- GSD Plan Phase
- GSD Verify Work
- Browser & Playwright Integration
- Debug File Protocol
- Hypothesis Testing
- TDD Execution
- Deviation Rules
- GSD Init Repo
- GSD Map Codebase
- GSD Roadmap
- GSD Checkpoints Reference
- GSD Continuation Format Reference
- GSD Git Integration Reference
- GSD Questioning Reference
- GSD TDD Reference
- GSD UI Brand Reference
- GSD Verification Patterns
- GSD Brownfield Workflow
- GSD Checkpoint Workflow
- GSD Debug Workflow
- GSD Execute Phase Workflow
- GSD New Project Workflow
- GSD Research Workflow
- Phase Tracker — Elder-Care Cognitive Companion (SIH26003)
- Examples
- State Updates
- GSD Add Phase
- GSD Add Todo
- GSD Audit Milestone
- GSD Check Todos
- GSD Complete Checkpoint
- GSD Complete Milestone
- GSD Continue Phase
- GSD Create Checkpoint
- GSD Discuss Phase
- GSD Help
- GSD Insert Phase
- GSD Integrate
- GSD List Phase Assumptions
- GSD New Milestone
- GSD Pause Work
- GSD Plan Milestone Gaps
- GSD Progress
- GSD Remove Phase
- GSD Research Phase
- GSD Research Project
- GSD Resume Work
- GSD Review Plan
- GSD Synthesize
- GSD Update Checkpoint
- GSD Update
- GSD Whats New
- GSD Complete Milestone Workflow
- GSD Diagnose Issues Workflow
- GSD Discovery Phase Workflow
- GSD Discuss Phase Workflow
- GSD Execute Plan Workflow
- GSD List Phase Assumptions Workflow
- GSD Resume Project Workflow
- GSD Transition Workflow
- GSD Verify Phase Workflow
- GSD Verify Work Workflow
- Structured Returns
- Authentication Gates
- Execution Patterns
- Elder-Care Backend
- Elder-Care Mobile App
- Phase 1: Repository Scaffold + Data Models
- opencode.json
- Final Commit
- Show history
- graphify.js
- AGENTS.md
- game_analytics_engine_test.dart
- game_labels.dart
- Game Assets — To Be Sourced/Commissioned

## God Nodes (most connected - your core abstractions)
1. `User` - 99 edges
2. `PatientProfile` - 52 edges
3. `GameSession` - 47 edges
4. `ReminderEvent` - 41 edges
5. `GameTypeEnum` - 40 edges
6. `ReminderService` - 40 edges
7. `ComplianceService` - 38 edges
8. `ReminderStatusEnum` - 35 edges
9. `LLMClient` - 35 edges
10. `RAGService` - 35 edges

## Surprising Connections (you probably didn't know these)
- `Offline-First Gaming (Deep Sync Queue)` --semantically_similar_to--> `Offline-First Gaming + Sync Queue Architecture`  [INFERRED] [semantically similar]
  brainstorm-demo-features.html → CLAUDE.md
- `Voice Companion in Regional Languages` --semantically_similar_to--> `Voice Companion (Bhashini + Claude)`  [INFERRED] [semantically similar]
  brainstorm-demo-features.html → CLAUDE.md
- `AI-Powered Alert Engine (rule-based + LLM triage)` --semantically_similar_to--> `Reminder Escalation Thresholds`  [INFERRED] [semantically similar]
  brainstorm-demo-features.html → CLAUDE.md
- `Caregiver Mobile App (Lite)` --semantically_similar_to--> `Caregiver Dashboard on Flutter Web (shared models)`  [INFERRED] [semantically similar]
  brainstorm-demo-features.html → CLAUDE.md
- `eldercare_mobile (Patient Mobile App package)` --semantically_similar_to--> `eldercare_dashboard (Caregiver Web Dashboard package)`  [INFERRED] [semantically similar]
  mobile/pubspec.yaml → dashboard/pubspec.yaml

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Local dev stack (docker-compose: db + redis + backend)** — docker_compose_db, docker_compose_redis, docker_compose_backend [EXTRACTED 0.90]
- **Phase 11 DPDP compliance pass components** — docs_superpowers_plans_2026_09_05_remaining_roadmap_to_mvp_phase11_compliance_pass, docs_superpowers_plans_2026_09_05_remaining_roadmap_to_mvp_access_control_gaps, docs_superpowers_plans_2026_09_05_remaining_roadmap_to_mvp_sync_queue_consumer, docs_superpowers_plans_2026_09_05_remaining_roadmap_to_mvp_column_encryption [EXTRACTED 0.90]
- **Claude + Bhashini AI language layer (voice companion, multilingual, RAG share the LLM stack)** — claude_voice_companion, claude_multilingual_scope, phase_1_status_rag_pipeline [INFERRED 0.80]
- **Cognitive games engine composed of games, content, difficulty and logging** — phase2_summary_games_engine, phase2_summary_match_it, phase2_summary_routine_sequencing, phase2_summary_adaptive_difficulty, phase2_summary_ner_content_packs, phase2_summary_game_session_logging [INFERRED 0.85]
- **Offline-first gaming architecture (brainstorm → decision → games engine)** — brainstorm_demo_features_offline_first, claude_offline_first_sync, phase2_summary_games_engine [INFERRED 0.85]

## Communities (198 total, 14 thin omitted)

### Community 0 - "app_database.dart"
Cohesion: 0.01
Nodes (158): BoolColumn get, class PatientRoutineRow extends, class ReminderEventRow extends, ColumnFilters, ColumnOrderings, dart:io, DateTimeColumn get, GeneratedColumn (+150 more)

### Community 1 - "game_models.dart"
Cohesion: 0.03
Nodes (76): accuracyPct, actionData, actionType, avgResponseTimeMs, cardId, cards, completedAt, copyWith (+68 more)

### Community 2 - "AuthService"
Cohesion: 0.07
Nodes (49): verify_token(), get_current_user(), _parse_sub(), JWT 'sub' is a stringified UUID; normalize for UUID column comparison., Auth middleware exports., login(), AsyncSession, BaseModel (+41 more)

### Community 3 - "ReportService"
Cohesion: 0.06
Nodes (59): P7 — persisted weekly clinical summary (one per patient per week)., WeeklyReport, EncryptionService, AES-256 Fernet-based field level encryption., Encrypt sensitive clinical text., Decrypt ciphertext back to plaintext., Any, AsyncSession (+51 more)

### Community 4 - "shared_models.dart"
Cohesion: 0.04
Nodes (54): double?, acknowledgedAt, acknowledgmentMethod, attempts, avgResponseTimeMs, baselineFromApi, baselineToApi, cadence (+46 more)

### Community 5 - "games.py"
Cohesion: 0.07
Nodes (41): complete_game(), ContentItemIn, ContentPackCreate, ContentPackSummary, create_content_pack(), DifficultyEvaluationResponse, _ensure_owned_session(), evaluate_difficulty() (+33 more)

### Community 6 - "dashboard/lib/main.dart"
Cohesion: 0.03
Nodes (74): _ack, acknowledge, _addSchedule, _addScheduleRow, _Api, _auditLogs, _auditPanel, _baseUrl (+66 more)

### Community 7 - "api_service.dart"
Cohesion: 0.04
Nodes (46): dart:developer, int?, accessToken, acknowledgeAlert, acknowledgeReminder, ApiException, authToken, AuthTokens (+38 more)

### Community 8 - "dashboard/lib/theme/monad_theme.dart"
Cohesion: 0.04
Nodes (50): ash, blackPill, bluePill, cardPadding, cardShape, coral, crimson, display (+42 more)

### Community 9 - "mobile/lib/main.dart"
Cohesion: 0.05
Nodes (42): CaregiverDashboardApp, TrendChart, FormState, _api, _AuthGate, AuthScreen, _AuthScreenState, _busy (+34 more)

### Community 10 - "Architecture & Decisions (CLAUDE.md)"
Cohesion: 0.09
Nodes (46): CI Backend Job (tests + live PG smoke), Backend Python Dependencies, AI-Powered Alert Engine (rule-based + LLM triage), Caregiver Mobile App (Lite), Demo-Worthy Features Brainstorm, Achievement & Streak System, Offline-First Gaming (Deep Sync Queue), Voice Companion in Regional Languages (+38 more)

### Community 11 - "all_models.py"
Cohesion: 0.08
Nodes (56): Alembic environment configuration for Elder-Care platform., Run migrations in 'offline' mode — emits SQL to stdout., Run migrations against a live database., run_migrations_offline(), run_migrations_online(), CaregiverPatientLink, CognitiveBaselineEnum, DifficultyAdjustmentLog (+48 more)

### Community 12 - "mobile/lib/theme/monad_theme.dart"
Cohesion: 0.04
Nodes (49): ash, blackPill, bluePill, cardPadding, cardShape, coral, crimson, display (+41 more)

### Community 13 - "Components"
Cohesion: 0.05
Nodes (38): ABC Diatype Mono — Body text, navigation, buttons, badges, tags, and ALL UI strings. The monospace choice across every functional element gives the interface its technical-manual character — body copy at 16-20px reads as data, not marketing. Nav labels and badges use 18px uppercase with tighter tracking; small print and meta text use 12px uppercase. Weight 500 is reserved for emphasized UI labels. · `--font-abc-diatype-mono`, Agent Prompt Guide, Announcement Bar, Border Radius, Components, CSS Custom Properties, Do, Do's and Don'ts (+30 more)

### Community 14 - "LLMClient"
Cohesion: 0.10
Nodes (27): detect_provider(), LLMClient, LLMServiceError, AsyncBaseTransport, Exception, Minimal LLM client shared by services (OpenRouter free tier or Anthropic). Used…, Drop paid slugs when free-only mode is on (OpenRouter only)., Return (url, headers, payload) for the active provider. (+19 more)

### Community 15 - "RAGService"
Cohesion: 0.06
Nodes (54): _build_provider(), EmbeddingProvider, EmbeddingUnavailableError, get_embedding_provider(), HeuristicEmbeddingProvider, LocalSentenceTransformerProvider, OpenAIEmbeddingProvider, ABC (+46 more)

### Community 16 - "deps.py"
Cohesion: 0.12
Nodes (26): can_access_patient(), get_permission_tier(), load_patient(), AsyncSession, UUID, Auth + patient-access dependencies. - get_current_user: extracts the user from…, Resolve basic | clinical for this caller against this patient., Fetch a patient profile by id, or None. (+18 more)

### Community 17 - "VoiceCompanionService"
Cohesion: 0.13
Nodes (28): VoiceCompanionConfig, MockLanguageService, Deterministic local language provider for testing and offline development., CompanionServiceError, load_persona_prompt(), Any, AsyncSession, Exception (+20 more)

### Community 18 - "sync.py"
Cohesion: 0.12
Nodes (19): Security dependency helpers., Build a FastAPI dependency that enforces role-based access. Usage:…, require_role(), health_check(), lifespan(), Serve single-page application UI at root URL., Health check endpoint for load balancers., root() (+11 more)

### Community 19 - "game_analytics_engine.dart"
Cohesion: 0.05
Nodes (39): accuracyPct, accuracyScore, attentionScore, avgResponseTimeMs, CognitiveGameSession, cognitiveSpeedScore, correctMoves, difficultyLevel (+31 more)

### Community 20 - "ConversationStore"
Cohesion: 0.16
Nodes (13): ConversationStore, _demo(), Per-patient conversation history for the voice companion. Seam: Redis when…, Turn-taking memory keyed by patient id., reset_conversation_store_for_tests(), _patient_with_consent(), asyncio, P4 — persona file + Redis-backed per-patient conversation history. (+5 more)

### Community 21 - "match_it_service.dart"
Cohesion: 0.07
Nodes (29): double get, MatchItBoard, accuracyPct, attempts, board, cards, copyWith, correctMatches (+21 more)

### Community 22 - "User"
Cohesion: 0.16
Nodes (22): Base, User, me(), _baseline(), CaregiverLinkRequest, CaregiverLinkResponse, create_patient(), get_my_patient() (+14 more)

### Community 23 - "match_it_screen.dart"
Cohesion: 0.04
Nodes (46): MatchItCard, _api, _armStuckTimer, _bufferAndSend, _bufferedActions, build, card, cardBack (+38 more)

### Community 24 - "ComplianceService"
Cohesion: 0.08
Nodes (38): acknowledge_alert(), get_caregiver_patients(), get_patient_summary(), AsyncSession, UUID, Caregiver & Clinician Dashboard API Routes., Retrieve all patients linked to this caregiver / ASHA worker., Retrieve 7-day cognitive trends, reminder compliance, and active alerts for a… (+30 more)

### Community 25 - "routine_service.dart"
Cohesion: 0.07
Nodes (28): int get, RoutineBoard, accuracyPct, board, canPlaceMore, copyWith, correctPlacements, errors (+20 more)

### Community 26 - "auth_session.dart"
Cohesion: 0.08
Nodes (23): AuthStatus get, bool get, ChangeNotifier, dart:convert, UserModel, _applyTokens, AuthSession, AuthStatus (+15 more)

### Community 27 - "GSD Planner"
Cohesion: 0.04
Nodes (44): Building the Dependency Graph, Context Budget Rules, Context Section Rules, Core Responsibilities, Critical Rules, Dependency Graph, Dependency Graph Construction, Depth Calibration (+36 more)

### Community 28 - "app.js"
Cohesion: 0.10
Nodes (23): acknowledgeReminder(), acknowledgeReminderEvent(), checkCurrentUser(), closePatientPanels(), createReminderSchedule(), CULTURAL_ITEMS, flippedIndices, handleCardClick() (+15 more)

### Community 29 - "test_phase2_services.py"
Cohesion: 0.05
Nodes (40): ContentItem, ContentPack, generate_match_it_board(), list_content_packs(), Any, NER-Themed Content Packs & Match-It Board Generator. Seedable content packs…, Register (or replace) a themed set so caregivers/admins can add packs without a…, Return summary metadata for all registered content packs. (+32 more)

### Community 30 - "caregiver_dashboard_screen.dart"
Cohesion: 0.09
Nodes (23): _acknowledge, _adherence, _alerts, _api, build, _buildBody, CaregiverDashboardScreen, _CaregiverDashboardScreenState (+15 more)

### Community 31 - "routine_screen.dart"
Cohesion: 0.05
Nodes (39): ../games/game_analytics_engine.dart, ../games/game_labels.dart, ../games/game_visuals.dart, accent, _api, _armStuckTimer, _bufferAndSend, _bufferedActions (+31 more)

### Community 32 - "test_phase12_gates.py"
Cohesion: 0.17
Nodes (17): Config, Refuse to boot a production process with placeholder secrets or open CORS., Settings, _login(), _patient(), asyncio, Consent-scope, permission-tier, export, and production-boot gates., _register() (+9 more)

### Community 33 - "GSD Roadmapper"
Cohesion: 0.05
Nodes (39): Anti-Enterprise, Core Responsibilities, Coverage is Non-Negotiable, Coverage Validation, Critical Rules, Depth Calibration, Deriving Phase Success Criteria, Deriving Phases from Requirements (+31 more)

### Community 34 - "RoleEnum"
Cohesion: 0.10
Nodes (35): AlertFlag, Enum, str, RoleEnum, _build_provider(), ConsoleNotificationProvider, get_notification_provider(), LogOnlyFallbackProvider (+27 more)

### Community 35 - "reminders_screen.dart"
Cohesion: 0.10
Nodes (21): Map, build, createState, _error, _handleAcknowledge, _iconFor, initState, _justAcked (+13 more)

### Community 36 - "offline_sync_service.dart"
Cohesion: 0.05
Nodes (45): api_service.dart, ../config/app_config.dart, dart:async, dart:math, ../database/app_database.dart, apiV1, AppConfig, _defined (+37 more)

### Community 37 - "language.py"
Cohesion: 0.10
Nodes (24): ASRRequest, _get_provider(), _handle(), language_status(), BaseModel, HTTPException, Speech & Language Translation API Routes. Routes wrap the configured language…, Translate between NER regional languages and English. (+16 more)

### Community 38 - "voice_companion_screen.dart"
Cohesion: 0.06
Nodes (32): _assetDir, availableImages, face, GameVisuals, _iconFace, iconFor, positiveFeedback, selectionFeedback (+24 more)

### Community 39 - "test_language_service.py"
Cohesion: 0.20
Nodes (19): get_language_service(), Dependency injector for speech and language service. `provider` overrides…, _client(), asyncio, MockTransport, Phase 8 tests — Bhashini provider & factory selection., test_asr_payload_and_parse(), test_factory_auto_returns_mock_without_credentials() (+11 more)

### Community 40 - "AppDelegate"
Cohesion: 0.11
Nodes (14): Flutter, FlutterAppDelegate, FlutterImplicitEngineBridge, FlutterImplicitEngineDelegate, FlutterSceneDelegate, AppDelegate, Any, Bool (+6 more)

### Community 41 - "GameSession"
Cohesion: 0.06
Nodes (59): GameSession, GameTypeEnum, DifficultyStrategy, evaluate_difficulty(), get_recent_sessions(), _log_adjustment(), ABC, Any (+51 more)

### Community 42 - "LanguageServiceError"
Cohesion: 0.28
Nodes (7): BhashiniLanguageService, LanguageServiceError, AsyncBaseTransport, Exception, Walk nested ULCA response (dicts + list indexes); None if missing., Raised when a language provider cannot complete a request., Real Government of India Bhashini (ULCA) inference pipeline client.

### Community 43 - "Verification Process"
Cohesion: 0.06
Nodes (32): Core Philosophy, Create VERIFICATION.md, Critical Rules, Final Artifact Status, GSD Verifier, Level 1: Existence, Level 2: Substantive, Level 3: Wired (+24 more)

### Community 44 - "GSD Integration Checker"
Cohesion: 0.06
Nodes (31): 1. Endpoint Configuration, 2. Request/Response Flow, 3. Authentication & Authorization, 4. Data Persistence, 5. Error Handling, Authentication & Authorization, Core Responsibilities, Create VERIFICATION.md (+23 more)

### Community 45 - "reminder_scheduler.dart"
Cohesion: 0.12
Nodes (16): FlutterLocalNotificationsPlugin, cancelAll, cancelSchedule, initialize, _initialized, instance, _nextInstanceOf, _parseTimes (+8 more)

### Community 46 - "jobs.py"
Cohesion: 0.12
Nodes (35): alert_engine_pass(), _env_int(), generate_events(), main(), maintenance_once(), _next_sunday_midnight(), _periodic_loop(), AsyncSession (+27 more)

### Community 47 - "ensure_patient_access"
Cohesion: 0.19
Nodes (18): ensure_patient_access(), Resolve a patient profile and enforce no-implicit-access. 404 when the patient…, ConsentCreateRequest, ConsentResponse, export_patient_data(), grant_consent(), list_audit_logs(), list_patient_consents() (+10 more)

### Community 48 - "GSD Plan Checker"
Cohesion: 0.07
Nodes (27): 1. Task Completeness, 2. Dependency Correctness, 3. File Ownership, 4. Scope Sanity, 5. Must-Haves Derivation, Core Responsibilities, Create VERIFICATION-CHECKER.md, Critical Rules (+19 more)

### Community 49 - "_post"
Cohesion: 0.13
Nodes (29): ensure_clinical_access(), ensure_consent(), Purpose-limitation gate: 403 unless an active ConsentRecord covers the scope., Family caregivers on the basic tier cannot read clinical detail., logout(), Log out. JWT is stateless, so the client discards its tokens., Start a new game session for the patient profile bound to this account., start_game() (+21 more)

### Community 50 - "test_phase6_7_alerts_reports.py"
Cohesion: 0.20
Nodes (18): AlertSeverityEnum, AlertTriggerTypeEnum, AlertEngine, Any, AsyncSession, datetime, UUID, P6 — Alert Engine: rule evaluation that WRITES AlertFlags + notifies. Rules… (+10 more)

### Community 51 - "database.py"
Cohesion: 0.21
Nodes (10): AsyncClient, get_db(), AsyncSession, Dependency for FastAPI routes: provides async DB session., Database module alias., client(), db_session(), AsyncSession (+2 more)

### Community 52 - "Architecture & Decisions — Elder-Care Cognitive Companion Platform"
Cohesion: 0.07
Nodes (27): 1. MVP Cognitive Baseline, 2. Caregiver Dashboard: Flutter Web (Shared Models), 3. Offline-First Gaming + Sync Queue Architecture, 4. Voice Companion: Bhashini + LLM, 5. Reminder Escalation Thresholds, 6. Multilingual MVP Scope, 7. Authentication & Authorization, 8. Compliance (DPDP Act 2023) (+19 more)

### Community 53 - "test_api_routes.py"
Cohesion: 0.35
Nodes (12): _create_patient(), _login(), asyncio, API route tests — auth refresh, patient profiles + caregiver links, sync, games…, Phase 8-10 endpoints are mounted and auth-gated where required., Regression: games routes previously crashed with TypeError from require_role…, _register(), test_auth_refresh_flow() (+4 more)

### Community 54 - "dashboard/test/widget_test.dart"
Cohesion: 0.22
Nodes (7): main, main, package:eldercare_dashboard/main.dart, package:eldercare_mobile/models/game_models.dart, package:eldercare_mobile/models/shared_models.dart, package:flutter_test/flutter_test.dart, package:shared_preferences/shared_preferences.dart

### Community 55 - "pack_picker_screen.dart"
Cohesion: 0.12
Nodes (17): ../data/local_content_packs.dart, match_it_screen.dart, MaterialPageRoute, build, _api, build, createState, _difficulty (+9 more)

### Community 56 - "DataClass"
Cohesion: 0.26
Nodes (13): Insertable, UpdateCompanion, DataClass, GameActionRow, GameActionsCompanion, GameSessionRow, GameSessionsCompanion, PatientRoutineRow (+5 more)

### Community 57 - "List"
Cohesion: 0.15
Nodes (12): Color, CustomPainter, _TrendPainter, List, build, color, paint, shouldRepaint (+4 more)

### Community 58 - "RateLimitMiddleware"
Cohesion: 0.24
Nodes (5): RateLimitMiddleware, IP rate limiting — 100 req/min default (Phase 12). Uses Redis when reachable so…, BaseHTTPMiddleware, Request, Response

### Community 59 - "GSD Project Researcher"
Cohesion: 0.07
Nodes (26): ARCHITECTURE.md Template, Architecture Researcher, Core Responsibilities, Critical Rules, Document Templates, FEATURES.md Template, Features Researcher, Greenfield vs Subsequent Milestone (+18 more)

### Community 60 - "create_voice_config"
Cohesion: 0.27
Nodes (9): activate_voice_config(), ConfigResponse, create_voice_config(), list_voice_configs(), AsyncSession, HTTPException, List all voice companion system-prompt versions (oldest first)., Create a new versioned system prompt; optionally activate it. (+1 more)

### Community 61 - "dashboard/web/manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, prefer_related_applications, short_name (+2 more)

### Community 62 - "mobile/web/manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, prefer_related_applications, short_name (+2 more)

### Community 63 - "backend service (FastAPI)"
Cohesion: 0.33
Nodes (7): eldercare_dashboard (Caregiver Web Dashboard package), backend service (FastAPI), db service (PostgreSQL + pgvector), redis service (cache/queue), Phase 12: Production Hardening, RAG pipeline (chunk -> embed -> pgvector -> Claude), eldercare_mobile (Patient Mobile App package)

### Community 64 - "reminders.py"
Cohesion: 0.19
Nodes (18): acknowledge_event(), AcknowledgeEventRequest, Config, create_schedule(), CreateScheduleRequest, deactivate_schedule(), evaluate_escalations(), EventResponse (+10 more)

### Community 65 - "Remaining Roadmap to a Production-Ready MVP — SIH26003"
Cohesion: 0.07
Nodes (26): A. Current Status, Already available (50 routes, verified), B. Remaining Phases, C. Implementation Roadmap (ordered, dependency-aware), D. Architecture (target), E. RAG Requirements, F. Database Requirements, G. API Requirements (+18 more)

### Community 66 - "@DataClassName"
Cohesion: 0.48
Nodes (7): @DataClassName, GameActions, GameSessions, PatientRoutines, ReminderEvents, SyncQueue, Table

### Community 67 - "Get Shit Done (GSD) - Project Management System"
Cohesion: 0.08
Nodes (25): Agent Skills, Anti-Patterns to Avoid, Atomic Commits, Check Progress, Command Skills, Context Budgeting, Core Philosophy, Debug Issues (+17 more)

### Community 68 - "smoke_e2e.py"
Cohesion: 0.50
Nodes (4): check(), main(), End-to-end API smoke test against a live backend + real database. Usage:…, Assert an HTTP response; print FAIL (with detail) and return parsed body.

### Community 70 - "ReminderEvent"
Cohesion: 0.12
Nodes (40): escalation_scan(), Escalate unacknowledged reminders, send reprompts, mark misses, raise alerts.…, AcknowledgmentMethodEnum, ReminderEvent, ReminderSchedule, ReminderStatusEnum, ReminderTypeEnum, Any (+32 more)

### Community 71 - "AppDatabase"
Cohesion: 0.67
Nodes (3): _, @DriftDatabase, AppDatabase

### Community 72 - "DPDP Compliance Foundation (ConsentRecord + AuditLog)"
Cohesion: 0.67
Nodes (3): DPDP Compliance Foundation (ConsentRecord + AuditLog), Column-level AES-256 encryption at rest (unwired), Phase 11: DPDP Compliance Pass

### Community 88 - "Codebase Design"
Cohesion: 0.09
Nodes (21): 1. In-process, 2. Local-substitutable, 3. Remote but owned (Ports & Adapters), 4. True external (Mock), Deepening, Dependency categories, Seam discipline, Testing strategy: replace, don't layer (+13 more)

### Community 89 - "GSD Codebase Mapper"
Cohesion: 0.09
Nodes (22): ARCHITECTURE.md Template, CONCERNS.md Template, CONVENTIONS.md Template, Core Responsibilities, Critical Rules, Document Templates, Focus Areas, GSD Codebase Mapper (+14 more)

### Community 90 - "GSD Phase Researcher"
Cohesion: 0.09
Nodes (21): Codebase Context, Core Responsibilities, Critical Rules, GSD Phase Researcher, Philosophy, Process, Related Skills, Research Blocked (+13 more)

### Community 92 - "2026-09-04-phase1-scaffold-data-models.md"
Cohesion: 0.10
Nodes (20): Async engine, Backend, Bhashini (placeholder), Copy app code, Copy requirements and install, CORS middleware, Downgrade, Expose port (+12 more)

### Community 93 - "Smriti — AI-Powered Cognitive Gaming and Memory Assistance Platform"
Cohesion: 0.10
Nodes (20): 1. Cognitive Games, 2. Caregiver Dashboard, 3. Reminders, 4. Voice Companion, 5. Text-to-Speech & Speech-to-Text, 6. Multilingual Support (NER Languages), 7. Offline Support, 🧠 About the Project (+12 more)

### Community 94 - "GSD Research Synthesizer"
Cohesion: 0.10
Nodes (19): Core Responsibilities, Critical Rules, Downstream Consumer, GSD Research Synthesizer, Process, Related Skills, Step 1: Read Research Files, Step 2: Synthesize Executive Summary (+11 more)

### Community 95 - "HTML Report Format"
Cohesion: 0.10
Nodes (18): Call-graph collapse, Candidate card, Cross-section (good for layered shallowness), Diagram patterns, Hand-built boxes-and-arrows (when Mermaid's layout fights you), Header, HTML Report Format, Mass diagram (good for "interface as wide as implementation") (+10 more)

### Community 97 - "Shell Patterns for execute"
Cohesion: 0.12
Nodes (15): Analyze access logs, Build Output Filtering, Capture build errors only, Commit activity analysis, Directory Size and Structure Analysis, Disk usage investigation, Filter application logs by severity, Git Analysis (+7 more)

### Community 98 - "Process"
Cohesion: 0.12
Nodes (15): Core Responsibilities, Decision gate:**, GSD New Project, Phase 1: Setup, Phase 2: Brownfield Offer, Phase 3: Deep Questioning, Phase 4: Workflow Preferences, Phase 5: Research Decision (+7 more)

### Community 99 - "JavaScript / TypeScript Patterns for execute"
Cohesion: 0.13
Nodes (14): Analyze a large JSON config file, API Response Processing, Dependency audit, Diff two JSON files, Fetch and summarize a REST API, File Content Parsing, JavaScript / TypeScript Patterns for execute, JSON Data Analysis (+6 more)

### Community 101 - "Python Patterns for execute"
Cohesion: 0.14
Nodes (13): Analyze a CSV file, Analyze a large JSON dataset, Compare two source files, CSV / Log File Analysis, Data Processing with json Module, Extract TODOs and FIXMEs from codebase, File Comparison, Find duplicate content across files (+5 more)

### Community 103 - "Deployment Guide — Elder-Care Cognitive Companion (SIH26003)"
Cohesion: 0.14
Nodes (13): Architecture overview, Backend, Dashboard (Flutter Web), Database, Deployment Guide — Elder-Care Cognitive Companion (SIH26003), Environment variables, Local development, Mobile app (+5 more)

### Community 104 - "Context Mode: Default for All Large Output"
Cohesion: 0.15
Nodes (13): Anti-Patterns, Automatic Triggers, Context Mode: Default for All Large Output, Critical Rules, Decision Tree, External Documentation, Language Selection, MANDATORY RULE (+5 more)

### Community 106 - "Phase 1 Decisions"
Cohesion: 0.15
Nodes (13): 1. MVP Cognitive Baseline, 2. Caregiver Dashboard: Flutter Web, 3. Offline-First Gaming + Sync Queue, 4. Voice Companion (Bhashini + Claude), 5. Reminder Escalation Thresholds, 6. Multilingual MVP, 7. Authentication & Authorization, 8. Compliance (DPDP Act 2023) (+5 more)

### Community 107 - "Anti-Patterns: Common Mistakes with execute / execute_file"
Cohesion: 0.17
Nodes (10): 1. Using execute for Small Outputs (< 20 Lines), 2. Forgetting to Print Output, 3. Using Bash When JS/Python Would Be Cleaner, 4. Loading Entire Files into Context Then Processing, 5. Not Using JSON.stringify for Structured Output, 6. Timeout Too Short for Network Operations, 7. Not Using summary_prompt Effectively, 8. `ctx_execute` Captures, `ctx_search` Filters — Don't Merge the Layers (+2 more)

### Community 108 - "Elder-Care Cognitive Companion Platform"
Cohesion: 0.20
Nodes (10): Architecture, Contributing, Documentation, Elder-Care Cognitive Companion Platform, Features (Phases 2-12), Flutter App, License, Local Development (+2 more)

### Community 109 - "GSD Debugger"
Cohesion: 0.22
Nodes (8): Core Responsibilities, Default Mode (no flags), GSD Debugger, Mode Flags, Modes, Related Skills, Success Criteria, When to Use

### Community 110 - "Investigation Techniques"
Cohesion: 0.22
Nodes (9): Binary Search / Divide and Conquer, Comment Out Everything, Differential Debugging, Git Bisect, Investigation Techniques, Minimal Reproduction, Observability First, Rubber Duck Debugging (+1 more)

### Community 111 - "Ponytail"
Cohesion: 0.22
Nodes (8): Boundaries, Intensity, Output, Persistence, Ponytail, Rules, The ladder, When NOT to be lazy

### Community 112 - "extract_document_text"
Cohesion: 0.33
Nodes (8): _decode_text(), extract_document_text(), _extract_pdf(), _looks_like_pdf(), _looks_like_text(), Document text extraction for RAG ingestion (PDF / plain text / markdown).…, Extract plaintext from an uploaded document's bytes. PDF via pypdf (pure…, Heuristic: decode-able as UTF-8 and mostly printable characters.

### Community 113 - "GSD Executor"
Cohesion: 0.25
Nodes (7): Completion Format, Continuation Handling, Core Responsibilities, Critical Rules, GSD Executor, Success Criteria, When to Use

### Community 114 - "Summary Creation"
Cohesion: 0.25
Nodes (8): Frontmatter Population, Include Authentication Gates Section If Any Occurred, Include Deviation Documentation, Location, One-Liner Must Be SUBSTANTIVE, Summary Creation, Title Format, Use Template

### Community 115 - "GSD Execute Phase"
Cohesion: 0.25
Nodes (7): Deviation Handling, GSD Execute Phase, Process, Related Skills, Success Criteria, Wave Execution Rules, When to Use

### Community 116 - "test_document_upload.py"
Cohesion: 0.50
Nodes (7): _clinician_with_patient(), asyncio, P5 — document file upload: PDF/text extraction feeds the existing RAG ingest.…, test_upload_real_pdf(), test_upload_rejects_empty_file(), test_upload_rejects_unsupported_type(), test_upload_text_file_ingests_and_answers()

### Community 117 - "dashboard_service.py"
Cohesion: 0.18
Nodes (12): DashboardService, Any, AsyncSession, UUID, Caregiver & Clinician Dashboard Analytics Service. Provides: - Multi-patient…, List all patients linked to this caregiver / ASHA worker with active status., Aggregate patient engagement, cognitive trends, compliance, and active alerts., asyncio (+4 more)

### Community 118 - "Checkpoint Types"
Cohesion: 0.29
Nodes (7): After Checkpoint, Checkpoint Format, Checkpoint Types, decision, human-action, human-verify, When to Return Checkpoints

### Community 119 - "Philosophy"
Cohesion: 0.29
Nodes (7): Cognitive Biases to Avoid, Foundation Principles, Meta-Debugging: Your Own Code, Philosophy, Systematic Investigation Disciplines, User = Reporter, Claude = Investigator, When to Restart

### Community 120 - "Verification Patterns"
Cohesion: 0.29
Nodes (7): Environment Verification, Regression Testing, Reproduction Verification, Stability Testing, Test-First Debugging, Verification Patterns, What "Verified" Means

### Community 121 - "Task Commit Protocol"
Cohesion: 0.29
Nodes (7): 1. Identify Modified Files, 2. Stage Only Task-Related Files, 3. Determine Commit Type, 4. Craft Commit Message, 5. Record Commit Hash, Atomic Commit Benefits, Task Commit Protocol

### Community 122 - "Checkpoint Protocol"
Cohesion: 0.29
Nodes (7): After Checkpoint, checkpoint:decision (9% of checkpoints), checkpoint:human-action (1% - rare), checkpoint:human-verify (90% of checkpoints), Checkpoint Protocol, Checkpoint Types, STOP immediately.** Do not continue to next task.

### Community 123 - "GSD Debug"
Cohesion: 0.29
Nodes (6): GSD Debug, Investigation Techniques, Process, Related Skills, Success Criteria, When to Use

### Community 124 - "GSD Plan Phase"
Cohesion: 0.29
Nodes (6): GSD Plan Phase, Output Documents, Process, Related Skills, Success Criteria, When to Use

### Community 125 - "GSD Verify Work"
Cohesion: 0.29
Nodes (6): GSD Verify Work, Process, Related Skills, Success Criteria, Verification Checklist, When to Use

### Community 128 - "Browser & Playwright Integration"
Cohesion: 0.33
Nodes (6): Browser & Playwright Integration, CRITICAL: Why `filename` + `path` is mandatory, Key Rule, Workflow A: Snapshot → File → Index → Search (multiple queries), Workflow B: Snapshot → File → Execute File (one-shot extraction), Workflow C: Console & Network (save to file if large)

### Community 129 - "Debug File Protocol"
Cohesion: 0.33
Nodes (6): Debug File Protocol, File Location, File Structure, Resume Behavior, Status Transitions, Update Rules

### Community 130 - "Hypothesis Testing"
Cohesion: 0.33
Nodes (6): Decision Point: When to Act, Evidence Quality, Experimental Design Framework, Falsifiability Requirement, Forming Hypotheses, Hypothesis Testing

### Community 131 - "TDD Execution"
Cohesion: 0.33
Nodes (6): 1. Check Test Infrastructure (if first TDD task), 2. RED - Write Failing Test, 3. GREEN - Implement to Pass, 4. REFACTOR (if needed), Error Handling, TDD Execution

### Community 132 - "Deviation Rules"
Cohesion: 0.33
Nodes (6): Deviation Rules, RULE 1: Auto-Fix Bugs, RULE 2: Auto-Add Missing Critical Functionality, RULE 3: Auto-Fix Blocking Issues, RULE 4: Ask About Architectural Changes, RULE PRIORITY

### Community 133 - "GSD Init Repo"
Cohesion: 0.33
Nodes (5): GSD Init Repo, Output Structure, Process, Success Criteria, When to Use

### Community 134 - "GSD Map Codebase"
Cohesion: 0.33
Nodes (5): GSD Map Codebase, Output Documents, Process, Success Criteria, When to Use

### Community 135 - "GSD Roadmap"
Cohesion: 0.33
Nodes (5): GSD Roadmap, Output Documents, Process, Success Criteria, When to Use

### Community 136 - "GSD Checkpoints Reference"
Cohesion: 0.33
Nodes (5): Best Practices, Checkpoint Contents, Checkpoint Types, GSD Checkpoints Reference, Success Criteria

### Community 137 - "GSD Continuation Format Reference"
Cohesion: 0.33
Nodes (5): Best Practices, GSD Continuation Format Reference, Session Continuation, State Preservation, Success Criteria

### Community 138 - "GSD Git Integration Reference"
Cohesion: 0.33
Nodes (5): Best Practices, Branch Strategy, Commit Patterns, GSD Git Integration Reference, Success Criteria

### Community 139 - "GSD Questioning Reference"
Cohesion: 0.33
Nodes (5): Best Practices, GSD Questioning Reference, Question Types, Success Criteria, When to Use

### Community 140 - "GSD TDD Reference"
Cohesion: 0.33
Nodes (5): Best Practices, GSD TDD Reference, Success Criteria, TDD Cycle, When to Use

### Community 141 - "GSD UI Brand Reference"
Cohesion: 0.33
Nodes (5): Best Practices, Brand Elements, GSD UI Brand Reference, Success Criteria, When to Use

### Community 142 - "GSD Verification Patterns"
Cohesion: 0.33
Nodes (5): Best Practices, GSD Verification Patterns, Success Criteria, Verification Types, When to Use

### Community 143 - "GSD Brownfield Workflow"
Cohesion: 0.33
Nodes (5): Entry Point, GSD Brownfield Workflow, Phases, Success Criteria, When to Use

### Community 144 - "GSD Checkpoint Workflow"
Cohesion: 0.33
Nodes (5): Entry Points, GSD Checkpoint Workflow, Phases, Success Criteria, When to Use

### Community 145 - "GSD Debug Workflow"
Cohesion: 0.33
Nodes (5): Entry Point, GSD Debug Workflow, Phases, Success Criteria, When to Use

### Community 146 - "GSD Execute Phase Workflow"
Cohesion: 0.33
Nodes (5): Entry Points, GSD Execute Phase Workflow, Phases, Success Criteria, When to Use

### Community 147 - "GSD New Project Workflow"
Cohesion: 0.33
Nodes (5): Entry Point, GSD New Project Workflow, Phases, Success Criteria, When to Use

### Community 148 - "GSD Research Workflow"
Cohesion: 0.33
Nodes (5): Entry Points, GSD Research Workflow, Phases, Success Criteria, When to Use

### Community 150 - "Phase Tracker — Elder-Care Cognitive Companion (SIH26003)"
Cohesion: 0.33
Nodes (5): Architecture references, Completed, How the code is verified, Phase Tracker — Elder-Care Cognitive Companion (SIH26003), Remaining

### Community 151 - "Examples"
Cohesion: 0.40
Nodes (5): Analyze test output, Check GitHub PRs, Debug an API endpoint, Examples, Read and analyze a large file

### Community 152 - "State Updates"
Cohesion: 0.40
Nodes (5): Calculate Progress Bar, Extract Decisions and Issues, State Updates, Update Current Position, Update Session Continuity

### Community 153 - "GSD Add Phase"
Cohesion: 0.40
Nodes (4): GSD Add Phase, Process, Success Criteria, When to Use

### Community 154 - "GSD Add Todo"
Cohesion: 0.40
Nodes (4): GSD Add Todo, Process, Success Criteria, When to Use

### Community 155 - "GSD Audit Milestone"
Cohesion: 0.40
Nodes (4): GSD Audit Milestone, Process, Success Criteria, When to Use

### Community 156 - "GSD Check Todos"
Cohesion: 0.40
Nodes (4): GSD Check Todos, Process, Success Criteria, When to Use

### Community 157 - "GSD Complete Checkpoint"
Cohesion: 0.40
Nodes (4): GSD Complete Checkpoint, Process, Success Criteria, When to Use

### Community 158 - "GSD Complete Milestone"
Cohesion: 0.40
Nodes (4): GSD Complete Milestone, Process, Success Criteria, When to Use

### Community 159 - "GSD Continue Phase"
Cohesion: 0.40
Nodes (4): GSD Continue Phase, Process, Success Criteria, When to Use

### Community 160 - "GSD Create Checkpoint"
Cohesion: 0.40
Nodes (4): GSD Create Checkpoint, Process, Success Criteria, When to Use

### Community 161 - "GSD Discuss Phase"
Cohesion: 0.40
Nodes (4): GSD Discuss Phase, Process, Success Criteria, When to Use

### Community 162 - "GSD Help"
Cohesion: 0.40
Nodes (4): GSD Help, Process, Success Criteria, When to Use

### Community 163 - "GSD Insert Phase"
Cohesion: 0.40
Nodes (4): GSD Insert Phase, Process, Success Criteria, When to Use

### Community 164 - "GSD Integrate"
Cohesion: 0.40
Nodes (4): GSD Integrate, Process, Success Criteria, When to Use

### Community 165 - "GSD List Phase Assumptions"
Cohesion: 0.40
Nodes (4): GSD List Phase Assumptions, Process, Success Criteria, When to Use

### Community 166 - "GSD New Milestone"
Cohesion: 0.40
Nodes (4): GSD New Milestone, Process, Success Criteria, When to Use

### Community 167 - "GSD Pause Work"
Cohesion: 0.40
Nodes (4): GSD Pause Work, Process, Success Criteria, When to Use

### Community 168 - "GSD Plan Milestone Gaps"
Cohesion: 0.40
Nodes (4): GSD Plan Milestone Gaps, Process, Success Criteria, When to Use

### Community 169 - "GSD Progress"
Cohesion: 0.40
Nodes (4): GSD Progress, Process, Success Criteria, When to Use

### Community 170 - "GSD Remove Phase"
Cohesion: 0.40
Nodes (4): GSD Remove Phase, Process, Success Criteria, When to Use

### Community 171 - "GSD Research Phase"
Cohesion: 0.40
Nodes (4): GSD Research Phase, Process, Success Criteria, When to Use

### Community 172 - "GSD Research Project"
Cohesion: 0.40
Nodes (4): GSD Research Project, Process, Success Criteria, When to Use

### Community 173 - "GSD Resume Work"
Cohesion: 0.40
Nodes (4): GSD Resume Work, Process, Success Criteria, When to Use

### Community 174 - "GSD Review Plan"
Cohesion: 0.40
Nodes (4): GSD Review Plan, Process, Success Criteria, When to Use

### Community 175 - "GSD Synthesize"
Cohesion: 0.40
Nodes (4): GSD Synthesize, Process, Success Criteria, When to Use

### Community 176 - "GSD Update Checkpoint"
Cohesion: 0.40
Nodes (4): GSD Update Checkpoint, Process, Success Criteria, When to Use

### Community 177 - "GSD Update"
Cohesion: 0.40
Nodes (4): GSD Update, Process, Success Criteria, When to Use

### Community 178 - "GSD Whats New"
Cohesion: 0.40
Nodes (4): GSD Whats New, Process, Success Criteria, When to Use

### Community 179 - "GSD Complete Milestone Workflow"
Cohesion: 0.40
Nodes (4): GSD Complete Milestone Workflow, Phases, Success Criteria, When to Use

### Community 180 - "GSD Diagnose Issues Workflow"
Cohesion: 0.40
Nodes (4): GSD Diagnose Issues Workflow, Phases, Success Criteria, When to Use

### Community 181 - "GSD Discovery Phase Workflow"
Cohesion: 0.40
Nodes (4): GSD Discovery Phase Workflow, Phases, Success Criteria, When to Use

### Community 182 - "GSD Discuss Phase Workflow"
Cohesion: 0.40
Nodes (4): GSD Discuss Phase Workflow, Phases, Success Criteria, When to Use

### Community 183 - "GSD Execute Plan Workflow"
Cohesion: 0.40
Nodes (4): GSD Execute Plan Workflow, Phases, Success Criteria, When to Use

### Community 184 - "GSD List Phase Assumptions Workflow"
Cohesion: 0.40
Nodes (4): GSD List Phase Assumptions Workflow, Phases, Success Criteria, When to Use

### Community 185 - "GSD Resume Project Workflow"
Cohesion: 0.40
Nodes (4): GSD Resume Project Workflow, Phases, Success Criteria, When to Use

### Community 186 - "GSD Transition Workflow"
Cohesion: 0.40
Nodes (4): GSD Transition Workflow, Phases, Success Criteria, When to Use

### Community 187 - "GSD Verify Phase Workflow"
Cohesion: 0.40
Nodes (4): GSD Verify Phase Workflow, Phases, Success Criteria, When to Use

### Community 188 - "GSD Verify Work Workflow"
Cohesion: 0.40
Nodes (4): GSD Verify Work Workflow, Phases, Success Criteria, When to Use

### Community 190 - "Structured Returns"
Cohesion: 0.50
Nodes (4): DEBUG COMPLETE (goal: find_and_fix), INVESTIGATION INCONCLUSIVE, ROOT CAUSE FOUND (goal: find_root_cause_only), Structured Returns

### Community 191 - "Authentication Gates"
Cohesion: 0.50
Nodes (4): Authentication Error Indicators, Authentication Gate Protocol, Authentication Gates, Example Return for Auth Gate

### Community 192 - "Execution Patterns"
Cohesion: 0.50
Nodes (4): Execution Patterns, Pattern A: Fully Autonomous (No Checkpoints), Pattern B: Has Checkpoints, Pattern C: Continuation (You Were Spawned to Continue)

### Community 193 - "Elder-Care Backend"
Cohesion: 0.50
Nodes (4): API Documentation, Elder-Care Backend, Setup, Testing

### Community 194 - "Elder-Care Mobile App"
Cohesion: 0.50
Nodes (4): Architecture, Elder-Care Mobile App, Setup, Testing

### Community 195 - "Phase 1: Repository Scaffold + Data Models"
Cohesion: 0.50
Nodes (4): Backend (`backend/`), File Structure, Global Constraints, Phase 1: Repository Scaffold + Data Models

### Community 196 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 197 - "Final Commit"
Cohesion: 0.67
Nodes (3): 1. Stage Execution Artifacts, 2. Commit Metadata, Final Commit

### Community 199 - "Show history"
Cohesion: 0.67
Nodes (3): Show history, Summary, Verification & Testing

### Community 203 - "game_analytics_engine_test.dart"
Cohesion: 0.33
Nodes (5): GameAnalyticsEngine, engine, main, _session, package:eldercare_mobile/games/game_analytics_engine.dart

### Community 206 - "game_labels.dart"
Cohesion: 0.40
Nodes (4): fallbackLanguage, GameLabels, of, static const String

### Community 207 - "Game Assets — To Be Sourced/Commissioned"
Cohesion: 0.50
Nodes (3): Audio — `assets/audio/` (soft, <1s), Game Assets — To Be Sourced/Commissioned, Illustrated card icons — `assets/games/icons/` (32 PNGs)

## Knowledge Gaps
- **1615 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `Config`, `matchCards`, `flippedIndices` (+1610 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 2126 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_post` connect `_post` to `reminders.py`, `AuthService`, `language.py`, `games.py`, `dashboard/lib/main.dart`, `ensure_patient_access`, `deps.py`, `sync.py`, `User`, `ComplianceService`, `create_voice_config`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `_get` connect `ComplianceService` to `language.py`, `games.py`, `dashboard/lib/main.dart`, `ensure_patient_access`, `_post`, `sync.py`, `User`, `create_voice_config`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `reminders.py`, `AuthService`, `RoleEnum`, `ReportService`, `games.py`, `language.py`, `ReminderEvent`, `GameSession`, `all_models.py`, `jobs.py`, `ensure_patient_access`, `deps.py`, `_post`, `sync.py`, `test_phase6_7_alerts_reports.py`, `ComplianceService`, `create_voice_config`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `User` (e.g. with `can_access_patient()` and `ensure_clinical_access()`) actually correct?**
  _`User` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `PatientProfile` (e.g. with `can_access_patient()` and `ensure_clinical_access()`) actually correct?**
  _`PatientProfile` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `GameSession` (e.g. with `_ensure_owned_session()` and `get_patient_stats()`) actually correct?**
  _`GameSession` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ReminderEvent` (e.g. with `escalation_scan()` and `acknowledge_event()`) actually correct?**
  _`ReminderEvent` has 16 INFERRED edges - model-reasoned connections that need verification._