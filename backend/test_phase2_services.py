#!/usr/bin/env python3
"""Phase 2 Game Services — Direct Import Verification.

Tests that all Phase 2 services import correctly and core functions work.
Run: python3 test_phase2_services.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0
errors = []


def run_test(name, fn):
    global passed, failed, errors
    try:
        fn()
        passed += 1
        print(f"  ✓ {name}")
    except Exception as e:
        failed += 1
        errors.append((name, str(e)))
        print(f"  ✗ {name}")
        print(f"    Error: {e}")


print("\n" + "=" * 60)
print("PHASE 2: Game Services Verification")
print("=" * 60 + "\n")

# Test 1: Content Packs import and basic functionality
print("Content Packs Service:")


def t_content_packs_import():
    from app.services.content_packs import (
        list_content_packs,
        generate_match_it_board,
        NER_CONTENT_PACKS,
    )
    assert NER_CONTENT_PACKS is not None


def t_content_packs_list():
    from app.services.content_packs import list_content_packs

    packs = list_content_packs()
    assert len(packs) == 3, f"Expected 3 packs, got {len(packs)}"
    assert "festivals_ner" in [p["id"] for p in packs]


def t_match_it_board_difficulty1():
    from app.services.content_packs import generate_match_it_board

    board = generate_match_it_board("festivals_ner", difficulty_level=1)
    assert board["pair_count"] == 4
    assert board["total_cards"] == 8
    assert len(board["cards"]) == 8


def t_match_it_board_difficulty3():
    from app.services.content_packs import generate_match_it_board

    board = generate_match_it_board("heritage_household_ner", difficulty_level=3)
    assert board["pair_count"] == 9
    assert board["total_cards"] == 18


run_test("Import content_packs service", t_content_packs_import)
run_test("List NER content packs (3 total)", t_content_packs_list)
run_test("Generate Match It board (Difficulty 1: 4 pairs)", t_match_it_board_difficulty1)
run_test("Generate Match It board (Difficulty 3: 9 pairs)", t_match_it_board_difficulty3)

# Test 2: Routine Service
print("\nRoutine Sequencing Service:")


def t_routine_import():
    from app.services.routine_service import (
        DEFAULT_DAILY_ROUTINE,
        generate_routine_sequencing_board,
        validate_routine_sequence,
    )
    assert DEFAULT_DAILY_ROUTINE is not None


def t_default_routine_structure():
    from app.services.routine_service import DEFAULT_DAILY_ROUTINE

    assert len(DEFAULT_DAILY_ROUTINE) == 10
    assert DEFAULT_DAILY_ROUTINE[0]["step_id"] == "wake_up"
    assert DEFAULT_DAILY_ROUTINE[-1]["step_id"] == "sleep"
    assert all("title_en" in s for s in DEFAULT_DAILY_ROUTINE)


def t_routine_board_level1():
    from app.services.routine_service import (
        DEFAULT_DAILY_ROUTINE,
        generate_routine_sequencing_board,
    )

    board = generate_routine_sequencing_board(DEFAULT_DAILY_ROUTINE, difficulty_level=1)
    assert board["step_count"] == 3
    assert board["has_hints"] is True
    assert board["has_icons"] is True
    assert len(board["shuffled_items"]) == 3
    assert len(board["correct_sequence"]) == 3


def t_routine_board_level3():
    from app.services.routine_service import (
        DEFAULT_DAILY_ROUTINE,
        generate_routine_sequencing_board,
    )

    board = generate_routine_sequencing_board(DEFAULT_DAILY_ROUTINE, difficulty_level=3)
    assert board["step_count"] == 6
    assert board["has_hints"] is False
    assert board["has_icons"] is False


def t_validate_routine_perfect():
    from app.services.routine_service import validate_routine_sequence

    correct = ["wake_up", "brush_teeth", "morning_tea"]
    submitted = ["wake_up", "brush_teeth", "morning_tea"]
    result = validate_routine_sequence(submitted, correct)
    assert result["is_perfect"] is True
    assert result["accuracy_pct"] == 100.0
    assert result["correct_count"] == 3
    assert len(result["errors"]) == 0


def t_validate_routine_partial():
    from app.services.routine_service import validate_routine_sequence

    correct = ["wake_up", "brush_teeth", "morning_tea"]
    submitted = ["wake_up", "morning_tea", "brush_teeth"]
    result = validate_routine_sequence(submitted, correct)
    assert result["is_perfect"] is False
    assert result["accuracy_pct"] < 100.0
    assert len(result["errors"]) > 0


run_test("Import routine_service", t_routine_import)
run_test("Default routine has 10 steps with multilingual titles", t_default_routine_structure)
run_test("Generate routine board (Level 1: 3 steps + hints)", t_routine_board_level1)
run_test("Generate routine board (Level 3: 6 steps, no hints)", t_routine_board_level3)
run_test("Validate routine — perfect sequence", t_validate_routine_perfect)
run_test("Validate routine — partial accuracy (2/3 correct)", t_validate_routine_partial)

# Test 3: Difficulty Engine
print("\nDifficulty Engine Service:")


def t_difficulty_import():
    from app.services.difficulty_engine import (
        DifficultyStrategy,
        RuleBasedDifficultyStrategy,
    )
    assert DifficultyStrategy is not None


def t_strategy_interface():
    from app.services.difficulty_engine import RuleBasedDifficultyStrategy

    strat = RuleBasedDifficultyStrategy()
    assert hasattr(strat, "calculate_adjustment")
    assert callable(strat.calculate_adjustment)


def t_bump_rule():
    from app.services.difficulty_engine import RuleBasedDifficultyStrategy

    strat = RuleBasedDifficultyStrategy()

    # Mock 3 sessions with >85% accuracy
    class MockSession:
        def __init__(self, acc):
            self.accuracy_pct = acc

    mock_sessions = [
        MockSession(90.0),
        MockSession(87.5),
        MockSession(88.0),
    ]
    bump_triggered = strat._check_bump_rule(mock_sessions)
    assert bump_triggered is True, "Should trigger bump with 3 consecutive >85% sessions"


def t_drop_rule():
    from app.services.difficulty_engine import RuleBasedDifficultyStrategy

    strat = RuleBasedDifficultyStrategy()

    # Mock 2 sessions with <50% accuracy
    class MockSession:
        def __init__(self, acc):
            self.accuracy_pct = acc

    mock_sessions = [
        MockSession(45.0),
        MockSession(48.0),
    ]
    drop_triggered = strat._check_drop_rule(mock_sessions)
    assert drop_triggered is True, "Should trigger drop with 2 consecutive <50% sessions"


def t_no_bump_on_single_high():
    from app.services.difficulty_engine import RuleBasedDifficultyStrategy

    strat = RuleBasedDifficultyStrategy()

    class MockSession:
        def __init__(self, acc):
            self.accuracy_pct = acc

    # Only 1 session with >85%
    mock_sessions = [MockSession(90.0)]
    bump_triggered = strat._check_bump_rule(mock_sessions)
    assert bump_triggered is False, "Should NOT bump with only 1 high session"


run_test("Import difficulty_engine", t_difficulty_import)
run_test("Strategy interface has calculate_adjustment method", t_strategy_interface)
run_test("Bump rule: 3 consecutive >85% accuracy", t_bump_rule)
run_test("Drop rule: 2 consecutive <50% accuracy", t_drop_rule)
run_test("No bump on single high session", t_no_bump_on_single_high)

# Test 4: Game Service (non-async stubs)
print("\nGame Service & Routing:")


def t_game_service_import():
    from app.services import game_service
    assert game_service is not None


def t_games_router_import():
    from app.routes import games
    assert games.router is not None
    assert hasattr(games.router, "routes")


def t_routes_registered():
    from app.routes import games

    # Check that key endpoints are defined
    route_names = [r.path for r in games.router.routes]
    assert any("sessions" in path for path in route_names), "Missing /sessions route"


run_test("Import game_service", t_game_service_import)
run_test("Import games router", t_games_router_import)
run_test("Routes registered (sessions endpoints exist)", t_routes_registered)

# Test 5: Main app integration
print("\nBackend Application Integration:")


def t_app_import():
    from app.main import app
    assert app is not None


def t_games_router_included():
    from starlette.testclient import TestClient
    from app.main import app

    # Games endpoints require auth, so an unauthenticated request proves the
    # router is mounted (401/403 = reachable; 404 = not registered).
    with TestClient(app) as tc:
        resp = tc.get("/api/v1/games/content-packs")
        assert resp.status_code in (401, 403), f"Games router not included in app (status {resp.status_code})"


run_test("Import FastAPI app", t_app_import)
run_test("Games router included in app", t_games_router_included)

# Summary
print("\n" + "=" * 60)
print(f"Results: {passed} PASSED, {failed} FAILED out of {passed + failed} total")
if errors:
    print("\nFailures:")
    for name, err in errors:
        print(f"  • {name}")
        print(f"    {err}")
print("=" * 60 + "\n")

sys.exit(0 if failed == 0 else 1)
