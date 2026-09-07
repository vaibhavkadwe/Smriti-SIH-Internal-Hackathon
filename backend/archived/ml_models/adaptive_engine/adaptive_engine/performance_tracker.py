from typing import Dict, List, Optional, Tuple
from collections import deque

from .models import GamePerformance, BaselineData, PatientReportData

DEFAULT_HISTORY_WINDOW: int = 5
DEFAULT_GAME_TYPE: str = "general"

HistoryKey = Tuple[str, str]


def _make_key(patient_id: str, game_type: Optional[str]) -> HistoryKey:
    gt = game_type if game_type is not None else DEFAULT_GAME_TYPE
    return (patient_id, gt)


class PerformanceTracker:
    def __init__(self, history_window: int = DEFAULT_HISTORY_WINDOW) -> None:
        if history_window < 3:
            raise ValueError("history_window must be at least 3 (for trend analysis)")
        self._history_window = history_window
        self._histories: Dict[HistoryKey, deque] = {}
        self._baselines: Dict[str, BaselineData] = {}
        self._reports: Dict[str, PatientReportData] = {}

    def register_baseline(
        self,
        patient_id: str,
        baseline: BaselineData,
        report: Optional[PatientReportData] = None,
    ) -> None:
        self._baselines[patient_id] = baseline
        if report is not None:
            self._reports[patient_id] = report

    def get_baseline(self, patient_id: str) -> Optional[BaselineData]:
        return self._baselines.get(patient_id)

    def get_report(self, patient_id: str) -> Optional[PatientReportData]:
        return self._reports.get(patient_id)

    def update_patient_performance(self, performance: GamePerformance) -> HistoryKey:
        key = _make_key(performance.patient_id, performance.game_type)
        if key not in self._histories:
            self._histories[key] = deque(maxlen=self._history_window)
        self._histories[key].append(performance)
        return key

    def get_recent_history(
        self,
        patient_id: str,
        game_type: Optional[str] = None,
        count: Optional[int] = None,
    ) -> List[GamePerformance]:
        key = _make_key(patient_id, game_type)
        history = self._histories.get(key)
        if history is None:
            return []
        if count is None:
            return list(history)
        if count <= 0:
            return []
        return list(history)[-count:]

    def history_size(
        self, patient_id: str, game_type: Optional[str] = None
    ) -> int:
        key = _make_key(patient_id, game_type)
        history = self._histories.get(key)
        return len(history) if history is not None else 0

    def game_types_for(self, patient_id: str) -> List[str]:
        result = []
        for (pid, gt) in self._histories.keys():
            if pid == patient_id:
                result.append(gt)
        return sorted(set(result))

    def clear_patient(self, patient_id: str) -> None:
        keys_to_drop = [k for k in self._histories.keys() if k[0] == patient_id]
        for k in keys_to_drop:
            self._histories.pop(k, None)
        self._baselines.pop(patient_id, None)
        self._reports.pop(patient_id, None)

    def clear_all(self) -> None:
        self._histories.clear()
        self._baselines.clear()
        self._reports.clear()

    def get_all_patients(self) -> List[str]:
        patient_ids = set()
        for (pid, _gt) in self._histories.keys():
            patient_ids.add(pid)
        for pid in self._baselines.keys():
            patient_ids.add(pid)
        return sorted(patient_ids)
