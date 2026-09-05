"""Self-contained test runner that doesn't depend on pytest being installed."""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

passed = 0
failed = 0
errors = []


def run_test(name, fn):
    global passed, failed, errors
    try:
        fn()
        passed += 1
        print(f"  PASS: {name}")
    except Exception as e:
        failed += 1
        errors.append((name, str(e)))
        print(f"  FAIL: {name} — {e}")


print("\n=== Running Phase 1 Self-Verification Tests ===\n")

# --- Auth Tests ---
print("Auth Service:")
from app.services.auth_service import AuthService
from app.config import settings


def t_pw_hash():
    pw = "secret123"
    h = AuthService.hash_password(pw)
    assert h != pw, "Hash equals plaintext"
    assert AuthService.verify_password(pw, h), "Verification failed"
    assert not AuthService.verify_password("wrong", h), "Wrong password verified"


def t_jwt_access():
    data = {"sub": "12345", "role": "family_caregiver"}
    tok = AuthService.create_access_token(data)
    p = AuthService.verify_token(tok)
    assert p["sub"] == "12345"
    assert p["role"] == "family_caregiver"


def t_jwt_refresh():
    tok = AuthService.create_refresh_token({"sub": "12345"})
    p = AuthService.verify_token(tok)
    assert p["sub"] == "12345"


def t_jwt_invalid():
    assert AuthService.verify_token("bad.token") is None


def t_config_langs():
    for lang in ["assamese", "bengali", "hindi", "english"]:
        assert lang in settings.LANGUAGE_SET, f"Missing {lang}"


run_test("Password hashing & verify", t_pw_hash)
run_test("JWT access token create & verify", t_jwt_access)
run_test("JWT refresh token create & verify", t_jwt_refresh)
run_test("Invalid JWT returns None", t_jwt_invalid)
run_test("NER language set configured", t_config_langs)

# --- Model Tests ---
print("\nSQLAlchemy Models:")
import uuid
from app.models.user import User, RoleEnum
from app.models.all_models import (
    PatientProfile, CaregiverPatientLink, GameSession,
    ReminderSchedule, ReminderEvent, AlertFlag, SyncQueue,
    CognitiveBaselineEnum, RelationshipTypeEnum, PermissionTierEnum,
    GameTypeEnum, ReminderTypeEnum, ReminderStatusEnum,
    AlertTriggerTypeEnum, AlertSeverityEnum,
    SyncResourceTypeEnum, SyncOperationEnum,
)
from app.models.compliance import ConsentRecord, AuditLog, ConsentTypeEnum, ConsentScopeEnum, AuditActionEnum


def t_user():
    u = User(phone="+919876543210", role=RoleEnum.PATIENT, preferred_language="assamese")
    assert u.role == RoleEnum.PATIENT


def t_patient():
    p = PatientProfile(name="Phukan Borah", cognitive_baseline=CognitiveBaselineEnum.MCI, region="Assam")
    assert p.name == "Phukan Borah"


def t_link():
    link = CaregiverPatientLink(
        caregiver_id=uuid.uuid4(),
        patient_id=uuid.uuid4(),
        relationship_type=RelationshipTypeEnum.FAMILY,
    )
    assert link.is_active is True


def t_consent():
    c = ConsentRecord(
        patient_id=uuid.uuid4(),
        consent_type=ConsentTypeEnum.HEALTH_DATA,
        grantor_id=uuid.uuid4(),
        scope=ConsentScopeEnum.GUARDIAN,
    )
    assert c.consent_type == ConsentTypeEnum.HEALTH_DATA


def t_audit():
    log = AuditLog(
        user_id=uuid.uuid4(),
        action=AuditActionEnum.READ,
        resource_type="patient_profile",
        resource_id=uuid.uuid4(),
    )
    assert log.action == AuditActionEnum.READ


def t_game():
    gs = GameSession(
        patient_id=uuid.uuid4(),
        game_type=GameTypeEnum.MATCH_IT,
        difficulty_level=2,
        correct_count=6,
    )
    assert gs.correct_count == 6


def t_sync():
    sq = SyncQueue(
        patient_id=uuid.uuid4(),
        resource_type=SyncResourceTypeEnum.GAME_SESSION,
        operation=SyncOperationEnum.CREATE,
        resource_id=uuid.uuid4(),
        payload={"score": 90},
    )
    assert sq.synced_at is None


run_test("User model + RoleEnum", t_user)
run_test("PatientProfile + CognitiveBaselineEnum", t_patient)
run_test("CaregiverPatientLink + RelationshipTypeEnum", t_link)
run_test("ConsentRecord + DPDP compliance scopes", t_consent)
run_test("AuditLog + AuditActionEnum", t_audit)
run_test("GameSession + GameTypeEnum", t_game)
run_test("SyncQueue (offline-first)", t_sync)

# --- Content Packs Tests ---
print("\nContent Packs Service:")
from app.services.content_packs import (
    list_content_packs,
    generate_match_it_board,
    NER_CONTENT_PACKS,
)


def t_content_packs_list():
    packs = list_content_packs()
    assert len(packs) == 3, f"Expected 3 packs, got {len(packs)}"
    pack_ids = [p["id"] for p in packs]
    assert "festivals_ner" in pack_ids
    assert "fruits_flora_ner" in pack_ids
    assert "heritage_household_ner" in pack_ids


def t_generate_board_easy():
    board = generate_match_it_board("festivals_ner", difficulty_level=1)
    assert board["pair_count"] == 4
    assert board["total_cards"] == 8
    assert len(board["cards"]) == 8


def t_generate_board_medium():
    board = generate_match_it_board("fruits_flora_ner", difficulty_level=2)
    assert board["pair_count"] == 6
    assert board["total_cards"] == 12


def t_generate_board_hard():
    board = generate_match_it_board("heritage_household_ner", difficulty_level=3)
    assert board["pair_count"] == 9
    assert board["total_cards"] == 18


run_test("List NER content packs", t_content_packs_list)
run_test("Generate Match It board (Easy: 4 pairs)", t_generate_board_easy)
run_test("Generate Match It board (Medium: 6 pairs)", t_generate_board_medium)
run_test("Generate Match It board (Hard: 9 pairs)", t_generate_board_hard)

# --- Routine Service Tests ---
print("\nRoutine Sequencing Service:")
from app.services.routine_service import (
    DEFAULT_DAILY_ROUTINE,
    generate_routine_sequencing_board,
    validate_routine_sequence,
)


def t_default_routine():
    assert len(DEFAULT_DAILY_ROUTINE) == 10
    assert DEFAULT_DAILY_ROUTINE[0]["step_id"] == "wake_up"
    assert DEFAULT_DAILY_ROUTINE[-1]["step_id"] == "sleep"


def t_generate_routine_board_level1():
    board = generate_routine_sequencing_board(DEFAULT_DAILY_ROUTINE, difficulty_level=1)
    assert board["step_count"] == 3
    assert board["has_hints"] is True
    assert board["has_icons"] is True
    assert len(board["shuffled_items"]) == 3
    assert len(board["correct_sequence"]) == 3


def t_generate_routine_board_level3():
    board = generate_routine_sequencing_board(DEFAULT_DAILY_ROUTINE, difficulty_level=3)
    assert board["step_count"] == 6
    assert board["has_hints"] is False
    assert board["has_icons"] is False


def t_validate_routine_perfect():
    correct = ["wake_up", "brush_teeth", "morning_tea"]
    submitted = ["wake_up", "brush_teeth", "morning_tea"]
    result = validate_routine_sequence(submitted, correct)
    assert result["is_perfect"] is True
    assert result["accuracy_pct"] == 100.0
    assert result["correct_count"] == 3


def t_validate_routine_partial():
    correct = ["wake_up", "brush_teeth", "morning_tea"]
    submitted = ["wake_up", "morning_tea", "brush_teeth"]
    result = validate_routine_sequence(submitted, correct)
    assert result["is_perfect"] is False
    assert result["accuracy_pct"] < 100.0
    assert len(result["errors"]) > 0


run_test("Default daily routine has 10 steps", t_default_routine)
run_test("Generate routine board (Level 1: 3 steps)", t_generate_routine_board_level1)
run_test("Generate routine board (Level 3: 6 steps)", t_generate_routine_board_level3)
run_test("Validate routine — perfect sequence", t_validate_routine_perfect)
run_test("Validate routine — partial accuracy", t_validate_routine_partial)

# --- Difficulty Engine Tests ---
print("\nDifficulty Engine Service:")
from app.services.difficulty_engine import RuleBasedDifficultyStrategy


def t_difficulty_strategy_interface():
    strat = RuleBasedDifficultyStrategy()
    assert hasattr(strat, "calculate_adjustment")
    assert callable(strat.calculate_adjustment)


def t_bump_rule_high_accuracy():
    strat = RuleBasedDifficultyStrategy()
    # Simulate 3 sessions with >85% accuracy
    mock_sessions = [
        type("MockSession", (), {"accuracy_pct": 90.0})(),
        type("MockSession", (), {"accuracy_pct": 87.5})(),
        type("MockSession", (), {"accuracy_pct": 88.0})(),
    ]
    bump_triggered = strat._check_bump_rule(mock_sessions)
    assert bump_triggered is True


def t_drop_rule_low_accuracy():
    strat = RuleBasedDifficultyStrategy()
    # Simulate 2 sessions with <50% accuracy
    mock_sessions = [
        type("MockSession", (), {"accuracy_pct": 45.0})(),
        type("MockSession", (), {"accuracy_pct": 48.0})(),
    ]
    drop_triggered = strat._check_drop_rule(mock_sessions)
    assert drop_triggered is True


run_test("Difficulty strategy interface exists", t_difficulty_strategy_interface)
run_test("Bump rule triggered on high accuracy", t_bump_rule_high_accuracy)
run_test("Drop rule triggered on low accuracy", t_drop_rule_low_accuracy)

# --- Summary ---
print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
if errors:
    print("Failures:")
    for name, err in errors:
        print(f"  - {name}: {err}")
print(f"{'='*40}\n")

sys.exit(1 if failed else 0)
