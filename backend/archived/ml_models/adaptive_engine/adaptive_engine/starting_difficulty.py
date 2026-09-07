from typing import Optional, Tuple

from .models import (
    BaselineData,
    PatientReportData,
    MIN_DIFFICULTY,
    MAX_DIFFICULTY,
    COGNITIVE_STATUS_WEIGHTS,
    CONCERN_PENALTY,
    BASELINE_COGNITIVE_FIELDS,
    DEFAULT_MISSING_BASELINE,
)


DEFAULT_REACTION_TIME: float = 2.5


def _rt_factor(rt: float) -> float:
    if rt >= 4.0:
        return 0.6
    if rt >= 3.0:
        return 0.75
    if rt >= 2.0:
        return 0.9
    if rt >= 1.2:
        return 1.0
    return 1.05


def _compute_baseline_composite(baseline: BaselineData) -> float:
    cognitive_values = [baseline.get_cognitive_value(a) for a in BASELINE_COGNITIVE_FIELDS]
    cognitive_avg = sum(cognitive_values) / len(cognitive_values)

    rt = baseline.baseline_reaction_time
    if rt is None:
        rt = DEFAULT_REACTION_TIME

    return cognitive_avg * _rt_factor(rt)


def _apply_report_adjustments(
    base_score: float, report: Optional[PatientReportData]
) -> float:
    if report is None:
        return base_score

    adjusted = base_score

    if report.cognitive_status is not None:
        weight = COGNITIVE_STATUS_WEIGHTS.get(report.cognitive_status, 1.0)
        adjusted *= weight

    if report.memory_concern:
        adjusted *= 1.0 - CONCERN_PENALTY
    if report.attention_concern:
        adjusted *= 1.0 - CONCERN_PENALTY
    if report.reasoning_concern:
        adjusted *= 1.0 - CONCERN_PENALTY

    return adjusted


def _score_to_difficulty(adjusted_score: float) -> int:
    if adjusted_score >= 82:
        return 5
    if adjusted_score >= 67:
        return 4
    if adjusted_score >= 50:
        return 3
    if adjusted_score >= 32:
        return 2
    return 1


def _clamp_difficulty(difficulty: int) -> int:
    return max(MIN_DIFFICULTY, min(MAX_DIFFICULTY, difficulty))


def determine_starting_difficulty(
    baseline: BaselineData,
    report: Optional[PatientReportData] = None,
) -> Tuple[int, float, float]:
    composite = _compute_baseline_composite(baseline)
    adjusted = _apply_report_adjustments(composite, report)
    difficulty = _score_to_difficulty(adjusted)
    return (_clamp_difficulty(difficulty), round(composite, 2), round(adjusted, 2))
