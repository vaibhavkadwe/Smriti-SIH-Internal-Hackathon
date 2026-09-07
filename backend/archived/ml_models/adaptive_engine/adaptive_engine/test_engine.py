import unittest

from adaptive_engine import (
    AdaptiveEngine,
    BaselineData,
    PatientReportData,
    GamePerformance,
    DecisionType,
    PerformanceTrend,
)
from adaptive_engine.models import MIN_DIFFICULTY, MAX_DIFFICULTY


class TestBaselineValidation(unittest.TestCase):
    def test_invalid_baseline_score_raises(self):
        with self.assertRaises(ValueError):
            BaselineData("P", 101, 50, 50, 50, 2.0)
        with self.assertRaises(ValueError):
            BaselineData("P", -1, 50, 50, 50, 2.0)

    def test_provided_valid_values_pass(self):
        b = BaselineData("P", 60, 70, 80, 75, 2.0)
        self.assertEqual(b.baseline_memory, 60)
        self.assertEqual(b.baseline_reaction_time, 2.0)

    def test_all_fields_optional_except_patient_id(self):
        b = BaselineData(patient_id="P-PARTIAL")
        self.assertIsNone(b.baseline_memory)
        self.assertIsNone(b.baseline_attention)
        self.assertIsNone(b.baseline_reasoning)
        self.assertIsNone(b.baseline_processing_speed)
        self.assertIsNone(b.baseline_reaction_time)

    def test_partial_baseline_is_valid(self):
        b = BaselineData(
            patient_id="P",
            baseline_memory=65,
            baseline_reasoning=None,
            baseline_processing_speed=60,
        )
        self.assertEqual(b.baseline_memory, 65)
        self.assertIsNone(b.baseline_attention)
        self.assertIsNone(b.baseline_reasoning)
        self.assertEqual(b.baseline_processing_speed, 60)
        self.assertIsNone(b.baseline_reaction_time)

    def test_invalid_baseline_rt_raises_only_when_provided(self):
        with self.assertRaises(ValueError):
            BaselineData("P", None, None, None, None, -1)
        with self.assertRaises(ValueError):
            BaselineData("P", None, None, None, None, 0)
        ok = BaselineData("P", None, None, None, None, None)
        self.assertIsNone(ok.baseline_reaction_time)

    def test_missing_value_uses_default_through_getter(self):
        b = BaselineData("P")
        self.assertEqual(b.get_cognitive_value("baseline_memory"), 50.0)
        b2 = BaselineData("P2", baseline_memory=70)
        self.assertEqual(b2.get_cognitive_value("baseline_memory"), 70.0)
        self.assertEqual(b2.get_cognitive_value("baseline_attention"), 50.0)

    def test_invalid_report_status_raises(self):
        with self.assertRaises(ValueError):
            PatientReportData(cognitive_status="unknown")

    def test_report_all_none_ok(self):
        r = PatientReportData()
        self.assertIsNone(r.cognitive_status)


class TestStartingDifficulty(unittest.TestCase):
    def setUp(self):
        self.engine = AdaptiveEngine()

    def test_strong_patient_gets_high_difficulty(self):
        result = self.engine.determine_starting_difficulty(
            {
                "patient_id": "P-STRONG",
                "baseline_memory": 90,
                "baseline_attention": 88,
                "baseline_reasoning": 92,
                "baseline_processing_speed": 95,
                "baseline_reaction_time": 1.0,
            }
        )
        self.assertIn(result["starting_difficulty"], [4, 5])

    def test_weak_patient_gets_low_difficulty(self):
        result = self.engine.determine_starting_difficulty(
            {
                "patient_id": "P-WEAK",
                "baseline_memory": 25,
                "baseline_attention": 30,
                "baseline_reasoning": 22,
                "baseline_processing_speed": 28,
                "baseline_reaction_time": 4.5,
            },
            {"cognitive_status": "severe"},
        )
        self.assertIn(result["starting_difficulty"], [1, 2])

    def test_mid_patient_gets_mid_difficulty(self):
        result = self.engine.determine_starting_difficulty(
            {
                "patient_id": "P-MID",
                "baseline_memory": 65,
                "baseline_attention": 70,
                "baseline_reasoning": 55,
                "baseline_processing_speed": 60,
                "baseline_reaction_time": 2.5,
            }
        )
        self.assertIn(result["starting_difficulty"], [2, 3, 4])

    def test_report_lowers_starting_difficulty(self):
        baseline_core = {
            "baseline_memory": 72,
            "baseline_attention": 72,
            "baseline_reasoning": 72,
            "baseline_processing_speed": 72,
            "baseline_reaction_time": 2.0,
        }
        no_report = self.engine.determine_starting_difficulty(
            {"patient_id": "A", **baseline_core}
        )
        with_report = self.engine.determine_starting_difficulty(
            {"patient_id": "B", **baseline_core},
            {
                "cognitive_status": "moderate",
                "memory_concern": True,
                "attention_concern": True,
                "reasoning_concern": True,
            },
        )
        self.assertLessEqual(
            with_report["starting_difficulty"], no_report["starting_difficulty"]
        )

    def test_difficulty_within_range_full_baseline(self):
        for mem in range(0, 101, 10):
            result = self.engine.determine_starting_difficulty(
                {
                    "patient_id": f"P-{mem}",
                    "baseline_memory": mem,
                    "baseline_attention": mem,
                    "baseline_reasoning": mem,
                    "baseline_processing_speed": mem,
                    "baseline_reaction_time": 2.0,
                }
            )
            self.assertGreaterEqual(result["starting_difficulty"], MIN_DIFFICULTY)
            self.assertLessEqual(result["starting_difficulty"], MAX_DIFFICULTY)

    def test_empty_baseline_still_works(self):
        result = self.engine.determine_starting_difficulty(
            {"patient_id": "P-NOTHING"}
        )
        self.assertGreaterEqual(result["starting_difficulty"], MIN_DIFFICULTY)
        self.assertLessEqual(result["starting_difficulty"], MAX_DIFFICULTY)

    def test_partial_baseline_works_via_dict(self):
        result = self.engine.determine_starting_difficulty(
            {
                "patient_id": "P-PART",
                "baseline_memory": 60,
                "baseline_reaction_time": 2.2,
            }
        )
        self.assertIn(result["starting_difficulty"], [2, 3])

    def test_partial_baseline_plus_report(self):
        result = self.engine.determine_starting_difficulty(
            {"patient_id": "P-R", "baseline_memory": 60},
            {"cognitive_status": "mild", "memory_concern": True},
        )
        self.assertGreaterEqual(result["starting_difficulty"], MIN_DIFFICULTY)
        self.assertLessEqual(result["starting_difficulty"], MAX_DIFFICULTY)


class TestPerformanceTracker(unittest.TestCase):
    def setUp(self):
        self.engine = AdaptiveEngine()

    def _add(self, pid, gt, diff, acc, mistakes=2, rt=2.0, ct=40):
        return self.engine.update_patient_performance(
            {
                "patient_id": pid,
                "game_type": gt,
                "current_difficulty": diff,
                "accuracy": acc,
                "mistakes": mistakes,
                "reaction_time": rt,
                "completion_time": ct,
            }
        )

    def test_tracks_per_game_type_isolated(self):
        self._add("A", "memory", 2, 80)
        self._add("A", "attention", 3, 60)
        self._add("A", "memory", 2, 85)
        self.assertEqual(
            len(self.engine.get_patient_history("A", game_type="memory")), 2
        )
        self.assertEqual(
            len(self.engine.get_patient_history("A", game_type="attention")), 1
        )

    def test_history_doesnt_leak_across_game_types(self):
        self._add("X", "memory", 2, 90)
        self._add("X", "memory", 2, 91)
        self._add("X", "memory", 2, 92)
        self.assertEqual(
            len(self.engine.get_patient_history("X", game_type="reasoning")), 0
        )

    def test_window_size_slides_per_game_type(self):
        engine = AdaptiveEngine(history_window=3)
        for acc in [70, 72, 74, 76, 78]:
            engine.update_patient_performance(
                {
                    "patient_id": "X",
                    "game_type": "memory",
                    "current_difficulty": 2,
                    "accuracy": acc,
                    "mistakes": 2,
                    "reaction_time": 2.0,
                    "completion_time": 40,
                }
            )
        history = engine.get_patient_history("X", game_type="memory")
        self.assertEqual(len(history), 3)
        self.assertEqual([h["accuracy"] for h in history], [74, 76, 78])

    def test_window_slides_independently_per_game(self):
        engine = AdaptiveEngine(history_window=3)
        for acc in [10, 20, 30, 40]:
            engine.update_patient_performance(
                {
                    "patient_id": "Z",
                    "game_type": "memory",
                    "current_difficulty": 1,
                    "accuracy": acc,
                    "mistakes": 0,
                    "reaction_time": 2.0,
                    "completion_time": 40,
                }
            )
        for acc in [1, 2, 3, 4, 5]:
            engine.update_patient_performance(
                {
                    "patient_id": "Z",
                    "game_type": "attention",
                    "current_difficulty": 1,
                    "accuracy": acc,
                    "mistakes": 0,
                    "reaction_time": 2.0,
                    "completion_time": 40,
                }
            )
        mem = engine.get_patient_history("Z", game_type="memory")
        att = engine.get_patient_history("Z", game_type="attention")
        self.assertEqual([h["accuracy"] for h in mem], [20, 30, 40])
        self.assertEqual([h["accuracy"] for h in att], [3, 4, 5])

    def test_dataclass_inputs_also_work(self):
        gp = GamePerformance(
            patient_id="DC",
            game_type="memory",
            current_difficulty=2,
            accuracy=80.0,
            mistakes=1,
            reaction_time=2.0,
            completion_time=30.0,
        )
        self.engine.update_patient_performance(gp)
        history = self.engine.get_patient_history("DC", game_type="memory")
        self.assertEqual(history[0]["accuracy"], 80.0)

    def test_decide_next_difficulty_honors_game_type_param(self):
        for acc in [88, 90, 92, 89, 91]:
            self._add("U", "memory", 2, acc, mistakes=1, rt=1.8, ct=38)
        self._add("U", "reasoning", 2, 50, mistakes=8, rt=3.5, ct=90)
        mem_decision = self.engine.decide_next_difficulty("U", game_type="memory")
        rea_decision = self.engine.decide_next_difficulty("U", game_type="reasoning")
        self.assertEqual(mem_decision["decision"], DecisionType.INCREASE.value)
        self.assertIn(
            rea_decision["decision"],
            [DecisionType.DECREASE.value, DecisionType.MAINTAIN.value],
        )
        self.assertEqual(mem_decision["game_type"], "memory")
        self.assertEqual(rea_decision["game_type"], "reasoning")
        self.assertEqual(mem_decision["patient_id"], "U")
        self.assertEqual(rea_decision["patient_id"], "U")


class TestAdaptiveDecisions(unittest.TestCase):
    def setUp(self):
        self.engine = AdaptiveEngine()
        self.engine.determine_starting_difficulty(
            {
                "patient_id": "P",
                "baseline_memory": 60,
                "baseline_attention": 60,
                "baseline_reasoning": 60,
                "baseline_processing_speed": 60,
                "baseline_reaction_time": 2.0,
            }
        )

    def _feed(self, accuracies, game_type="memory", difficulty=2, mistakes=2, rt=2.0, ct=40):
        for acc in accuracies:
            self.engine.update_patient_performance(
                {
                    "patient_id": "P",
                    "game_type": game_type,
                    "current_difficulty": difficulty,
                    "accuracy": acc,
                    "mistakes": mistakes,
                    "reaction_time": rt,
                    "completion_time": ct,
                }
            )
        return self.engine.decide_next_difficulty("P", game_type=game_type)

    def test_consistently_high_accuracy_increases(self):
        decision = self._feed([88, 90, 92, 89, 91])
        self.assertEqual(decision["decision"], DecisionType.INCREASE.value)
        self.assertEqual(decision["recommended_difficulty"], 3)

    def test_consistently_low_accuracy_decreases(self):
        decision = self._feed([52, 50, 48, 54, 51], difficulty=3)
        self.assertEqual(decision["decision"], DecisionType.DECREASE.value)
        self.assertEqual(decision["recommended_difficulty"], 2)

    def test_mid_accuracy_maintains(self):
        decision = self._feed([72, 74, 70, 73, 71])
        self.assertEqual(decision["decision"], DecisionType.MAINTAIN.value)
        self.assertEqual(decision["recommended_difficulty"], 2)

    def test_single_very_weak_session_decreases(self):
        decision = self._feed([45], difficulty=3)
        self.assertEqual(decision["decision"], DecisionType.DECREASE.value)
        self.assertEqual(decision["recommended_difficulty"], 2)

    def test_min_difficulty_wont_decrease(self):
        decision = self._feed([40, 42, 38], difficulty=1)
        self.assertEqual(decision["decision"], DecisionType.MAINTAIN.value)
        self.assertEqual(decision["recommended_difficulty"], 1)

    def test_max_difficulty_wont_increase(self):
        decision = self._feed([90, 92, 94, 93, 95], difficulty=5)
        self.assertEqual(decision["decision"], DecisionType.MAINTAIN.value)
        self.assertEqual(decision["recommended_difficulty"], 5)

    def test_response_keys_match_spec(self):
        decision = self._feed([80, 82, 85])
        for key in [
            "decision",
            "current_difficulty",
            "recommended_difficulty",
            "performance_trend",
            "reason",
            "game_type",
            "patient_id",
        ]:
            self.assertIn(key, decision)
        self.assertIn(
            decision["decision"],
            [
                DecisionType.INCREASE.value,
                DecisionType.MAINTAIN.value,
                DecisionType.DECREASE.value,
            ],
        )
        self.assertIn(
            decision["performance_trend"],
            [t.value for t in PerformanceTrend],
        )

    def test_history_isolated_by_patient(self):
        self.engine.update_patient_performance(
            {
                "patient_id": "A",
                "game_type": "memory",
                "current_difficulty": 2,
                "accuracy": 95,
                "mistakes": 0,
                "reaction_time": 1.0,
                "completion_time": 30,
            }
        )
        empty_b = self.engine.decide_next_difficulty("B", game_type="memory")
        self.assertEqual(empty_b["current_difficulty"], MIN_DIFFICULTY)
        self.assertEqual(
            empty_b["performance_trend"], PerformanceTrend.INSUFFICIENT_DATA.value
        )

    def test_high_mistakes_alone_triggers_decrease_when_low_accuracy(self):
        decision = self._feed(
            [55, 54, 53],
            difficulty=3,
            mistakes=6,
        )
        self.assertEqual(decision["decision"], DecisionType.DECREASE.value)

    def test_mid_perf_with_improving_trend_near_threshold_increases(self):
        decision = self._feed(
            [78, 80, 82, 84, 86],
            difficulty=2,
            mistakes=2,
            rt=2.2,
        )
        self.assertIn(
            decision["decision"],
            [DecisionType.INCREASE.value, DecisionType.MAINTAIN.value],
        )


class TestBackwardsCompatDefaults(unittest.TestCase):
    def test_game_type_omitted_falls_back_to_general(self):
        engine = AdaptiveEngine()
        engine.determine_starting_difficulty(
            {
                "patient_id": "C",
                "baseline_memory": 70,
                "baseline_attention": 70,
                "baseline_reasoning": 70,
                "baseline_processing_speed": 70,
                "baseline_reaction_time": 2.0,
            }
        )
        for acc in [90, 92, 94]:
            engine.update_patient_performance(
                {
                    "patient_id": "C",
                    "game_type": "general",
                    "current_difficulty": 2,
                    "accuracy": acc,
                    "mistakes": 1,
                    "reaction_time": 2.0,
                    "completion_time": 40,
                }
            )
        d = engine.decide_next_difficulty("C")
        self.assertEqual(d["decision"], DecisionType.INCREASE.value)
        self.assertEqual(d["game_type"], "general")
        self.assertEqual(d["patient_id"], "C")


if __name__ == "__main__":
    unittest.main(verbosity=2)
