import json
from adaptive_engine import AdaptiveEngine


def print_section(title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def pp(data) -> None:
    print(json.dumps(data, indent=2, default=str))


def example_1_baseline_only() -> None:
    print_section("EXAMPLE 1: Starting Difficulty — Baseline Only (No Report)")

    engine = AdaptiveEngine()

    baseline = {
        "patient_id": "P001",
        "baseline_memory": 65,
        "baseline_attention": 70,
        "baseline_reasoning": 55,
        "baseline_processing_speed": 60,
        "baseline_reaction_time": 2.5,
    }

    result = engine.determine_starting_difficulty(baseline)
    pp(result)


def example_2_baseline_with_report() -> None:
    print_section("EXAMPLE 2: Starting Difficulty — Baseline + Patient Report")

    engine = AdaptiveEngine()

    baseline = {
        "patient_id": "P002",
        "baseline_memory": 72,
        "baseline_attention": 78,
        "baseline_reasoning": 68,
        "baseline_processing_speed": 74,
        "baseline_reaction_time": 1.9,
    }

    report = {
        "cognitive_status": "mild",
        "memory_concern": True,
        "attention_concern": False,
        "reasoning_concern": True,
    }

    result = engine.determine_starting_difficulty(baseline, report)
    pp(result)


def example_3_severe_cases() -> None:
    print_section("EXAMPLE 3: Starting Difficulty — Severe vs Strong")

    engine = AdaptiveEngine()

    severe = {
        "patient_id": "P-SEVERE",
        "baseline_memory": 25,
        "baseline_attention": 30,
        "baseline_reasoning": 22,
        "baseline_processing_speed": 28,
        "baseline_reaction_time": 4.5,
    }
    pp(engine.determine_starting_difficulty(severe, {"cognitive_status": "severe"}))

    strong = {
        "patient_id": "P-STRONG",
        "baseline_memory": 92,
        "baseline_attention": 88,
        "baseline_reasoning": 90,
        "baseline_processing_speed": 94,
        "baseline_reaction_time": 0.9,
    }
    pp(engine.determine_starting_difficulty(strong))


def example_4_adaptive_over_sessions() -> None:
    print_section("EXAMPLE 4: Adaptive Difficulty Over 5 Improving Sessions")

    engine = AdaptiveEngine()

    engine.determine_starting_difficulty(
        {
            "patient_id": "P010",
            "baseline_memory": 60,
            "baseline_attention": 65,
            "baseline_reasoning": 58,
            "baseline_processing_speed": 62,
            "baseline_reaction_time": 2.2,
        }
    )

    sessions = [
        {"current_difficulty": 2, "accuracy": 72, "mistakes": 4, "reaction_time": 2.4, "completion_time": 55},
        {"current_difficulty": 2, "accuracy": 78, "mistakes": 3, "reaction_time": 2.2, "completion_time": 52},
        {"current_difficulty": 2, "accuracy": 84, "mistakes": 2, "reaction_time": 2.0, "completion_time": 48},
        {"current_difficulty": 2, "accuracy": 89, "mistakes": 2, "reaction_time": 1.9, "completion_time": 45},
        {"current_difficulty": 2, "accuracy": 92, "mistakes": 1, "reaction_time": 1.8, "completion_time": 42},
    ]

    for i, s in enumerate(sessions, 1):
        perf = {"patient_id": "P010", "game_type": "memory", **s}
        print(f"\n--- Session {i} (played at diff {s['current_difficulty']}) ---")
        print("  Game Performance recorded:", engine.update_patient_performance(perf))
        decision = engine.decide_next_difficulty("P010")
        print("  Engine Decision:")
        pp(decision)


def example_5_decline_scenario() -> None:
    print_section("EXAMPLE 5: Adaptive Difficulty — Performance Declines Over Time")

    engine = AdaptiveEngine()

    engine.determine_starting_difficulty(
        {
            "patient_id": "P020",
            "baseline_memory": 50,
            "baseline_attention": 52,
            "baseline_reasoning": 48,
            "baseline_processing_speed": 50,
            "baseline_reaction_time": 2.8,
        }
    )

    sessions = [
        {"current_difficulty": 3, "accuracy": 70, "mistakes": 3, "reaction_time": 2.6, "completion_time": 60},
        {"current_difficulty": 3, "accuracy": 62, "mistakes": 5, "reaction_time": 2.9, "completion_time": 68},
        {"current_difficulty": 3, "accuracy": 54, "mistakes": 6, "reaction_time": 3.2, "completion_time": 74},
    ]

    for i, s in enumerate(sessions, 1):
        perf = {"patient_id": "P020", "game_type": "attention", **s}
        print(f"\n--- Session {i} (played at diff {s['current_difficulty']}) ---")
        print("  Game Performance recorded:", engine.update_patient_performance(perf))
        decision = engine.decide_next_difficulty("P020")
        print("  Engine Decision:")
        pp(decision)


def example_6_patient_history_and_summary() -> None:
    print_section("EXAMPLE 6: Inspecting Patient History & Summary")

    engine = AdaptiveEngine()

    engine.determine_starting_difficulty(
        {
            "patient_id": "P999",
            "baseline_memory": 70,
            "baseline_attention": 75,
            "baseline_reasoning": 68,
            "baseline_processing_speed": 72,
            "baseline_reaction_time": 2.0,
        },
        {
            "cognitive_status": "normal",
            "memory_concern": False,
            "attention_concern": False,
            "reasoning_concern": False,
        },
    )

    for acc, diff in [(82, 3), (86, 3), (90, 4)]:
        engine.update_patient_performance(
            {
                "patient_id": "P999",
                "game_type": "reasoning",
                "current_difficulty": diff,
                "accuracy": acc,
                "mistakes": 2,
                "reaction_time": 2.0,
                "completion_time": 45,
            }
        )

    print("\nPatient Summary:")
    pp(engine.get_patient_summary("P999"))

    print("\nAll Patients in Engine:", engine.list_patients())
    print("Reset P999:", engine.reset_patient("P999"))
    print("All Patients After Reset:", engine.list_patients())


def main() -> None:
    print("Adaptive Intelligence Engine — SIH26003 Cognitive Gaming")
    print("This module demonstrates the clean integration API for backend teammates.")

    example_1_baseline_only()
    example_2_baseline_with_report()
    example_3_severe_cases()
    example_4_adaptive_over_sessions()
    example_5_decline_scenario()
    example_6_patient_history_and_summary()

    print_section("INTEGRATION CHEAT SHEET")
    print("""
    1) First session for new patient:
         engine.determine_starting_difficulty(baseline_dict, [report_dict])
         -> returns {"starting_difficulty": 1..5, ...}

    2) After each game:
         engine.update_patient_performance(performance_dict)
         -> records the session (keeps last 5 per patient)

    3) Before next game:
         engine.decide_next_difficulty(patient_id)
         -> returns {"decision": INCREASE/MAINTAIN/DECREASE,
                     "recommended_difficulty": N,
                     "performance_trend": IMPROVING/STABLE/DECLINING,
                     "reason": "..."}
    """)


if __name__ == "__main__":
    main()
