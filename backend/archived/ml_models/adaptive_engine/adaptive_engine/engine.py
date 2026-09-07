from typing import Optional, Dict, Any, List, Union

from .models import (
    BaselineData,
    PatientReportData,
    GamePerformance,
    DifficultyDecision,
    PerformanceTrend,
    DecisionType,
    MIN_DIFFICULTY,
    MAX_DIFFICULTY,
)
from .starting_difficulty import determine_starting_difficulty
from .performance_tracker import (
    PerformanceTracker,
    DEFAULT_HISTORY_WINDOW,
    DEFAULT_GAME_TYPE,
)
from .adaptive_decision import decide_next_difficulty


class AdaptiveEngine:
    def __init__(self, history_window: int = DEFAULT_HISTORY_WINDOW) -> None:
        self._tracker = PerformanceTracker(history_window=history_window)

    def determine_starting_difficulty(
        self,
        baseline: Union[BaselineData, Dict[str, Any]],
        report: Optional[Union[PatientReportData, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        baseline_obj = self._coerce_baseline(baseline)
        report_obj = self._coerce_report(report)
        difficulty, composite, adjusted = determine_starting_difficulty(
            baseline_obj, report_obj
        )
        self._tracker.register_baseline(baseline_obj.patient_id, baseline_obj, report_obj)
        return {
            "patient_id": baseline_obj.patient_id,
            "starting_difficulty": difficulty,
            "baseline_composite_score": composite,
            "adjusted_score": adjusted,
            "min_difficulty": MIN_DIFFICULTY,
            "max_difficulty": MAX_DIFFICULTY,
        }

    def update_patient_performance(
        self,
        performance: Union[GamePerformance, Dict[str, Any]],
    ) -> Dict[str, Any]:
        perf_obj = self._coerce_performance(performance)
        self._tracker.update_patient_performance(perf_obj)
        history_size = self._tracker.history_size(
            perf_obj.patient_id, game_type=perf_obj.game_type
        )
        return {
            "patient_id": perf_obj.patient_id,
            "session_recorded": True,
            "history_size_for_game_type": history_size,
            "game_type": perf_obj.game_type,
            "difficulty_played": perf_obj.current_difficulty,
        }

    def decide_next_difficulty(
        self,
        patient_id: str,
        game_type: Optional[str] = None,
        session_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        sessions = self._tracker.get_recent_history(
            patient_id, game_type=game_type, count=session_count
        )
        baseline = self._tracker.get_baseline(patient_id)
        decision: DifficultyDecision = decide_next_difficulty(sessions, baseline)
        result = decision.to_dict()
        resolved_game_type = (
            game_type
            if game_type is not None
            else (
                sessions[-1].game_type
                if sessions
                else DEFAULT_GAME_TYPE
            )
        )
        result["game_type"] = resolved_game_type
        result["patient_id"] = patient_id
        return result

    def get_patient_history(
        self,
        patient_id: str,
        game_type: Optional[str] = None,
        count: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        sessions = self._tracker.get_recent_history(
            patient_id, game_type=game_type, count=count
        )
        return [
            {
                "patient_id": s.patient_id,
                "game_type": s.game_type,
                "current_difficulty": s.current_difficulty,
                "accuracy": s.accuracy,
                "mistakes": s.mistakes,
                "reaction_time": s.reaction_time,
                "completion_time": s.completion_time,
                "session_id": s.session_id,
                "timestamp": s.timestamp.isoformat(),
            }
            for s in sessions
        ]

    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        baseline = self._tracker.get_baseline(patient_id)
        report = self._tracker.get_report(patient_id)
        game_types = self._tracker.game_types_for(patient_id)
        per_game_history: Dict[str, List[Dict[str, Any]]] = {
            gt: self.get_patient_history(patient_id, game_type=gt) for gt in game_types
        }
        return {
            "patient_id": patient_id,
            "has_baseline": baseline is not None,
            "game_types_with_history": game_types,
            "baseline": (
                {
                    "memory": baseline.baseline_memory,
                    "attention": baseline.baseline_attention,
                    "reasoning": baseline.baseline_reasoning,
                    "processing_speed": baseline.baseline_processing_speed,
                    "reaction_time": baseline.baseline_reaction_time,
                }
                if baseline is not None
                else None
            ),
            "report": (
                {
                    "cognitive_status": report.cognitive_status,
                    "memory_concern": report.memory_concern,
                    "attention_concern": report.attention_concern,
                    "reasoning_concern": report.reasoning_concern,
                }
                if report is not None
                else None
            ),
            "history_by_game_type": {
                gt: {"size": len(h), "history": h}
                for gt, h in per_game_history.items()
            },
            "total_history_entries": sum(len(h) for h in per_game_history.values()),
        }

    def list_patients(self) -> List[str]:
        return self._tracker.get_all_patients()

    def reset_patient(self, patient_id: str) -> bool:
        existed = patient_id in (self._tracker.get_all_patients())
        self._tracker.clear_patient(patient_id)
        return existed

    def reset_all(self) -> None:
        self._tracker.clear_all()

    @staticmethod
    def _coerce_baseline(data: Union[BaselineData, Dict[str, Any]]) -> BaselineData:
        if isinstance(data, BaselineData):
            return data
        if isinstance(data, dict):
            def _opt_float(key: str) -> Optional[float]:
                value = data.get(key)
                if value is None:
                    return None
                return float(value)
            return BaselineData(
                patient_id=data["patient_id"],
                baseline_memory=_opt_float("baseline_memory"),
                baseline_attention=_opt_float("baseline_attention"),
                baseline_reasoning=_opt_float("baseline_reasoning"),
                baseline_processing_speed=_opt_float("baseline_processing_speed"),
                baseline_reaction_time=_opt_float("baseline_reaction_time"),
            )
        raise TypeError("baseline must be BaselineData or a dict")

    @staticmethod
    def _coerce_report(
        data: Optional[Union[PatientReportData, Dict[str, Any]]]
    ) -> Optional[PatientReportData]:
        if data is None:
            return None
        if isinstance(data, PatientReportData):
            return data
        if isinstance(data, dict):
            return PatientReportData(
                cognitive_status=data.get("cognitive_status"),
                memory_concern=data.get("memory_concern"),
                attention_concern=data.get("attention_concern"),
                reasoning_concern=data.get("reasoning_concern"),
            )
        raise TypeError("report must be PatientReportData, a dict, or None")

    @staticmethod
    def _coerce_performance(
        data: Union[GamePerformance, Dict[str, Any]]
    ) -> GamePerformance:
        if isinstance(data, GamePerformance):
            return data
        if isinstance(data, dict):
            return GamePerformance(
                patient_id=data["patient_id"],
                game_type=data.get("game_type", DEFAULT_GAME_TYPE),
                current_difficulty=int(data["current_difficulty"]),
                accuracy=float(data["accuracy"]),
                mistakes=int(data.get("mistakes", 0)),
                reaction_time=float(data["reaction_time"]),
                completion_time=float(data["completion_time"]),
                session_id=data.get("session_id"),
            )
        raise TypeError("performance must be GamePerformance or a dict")
