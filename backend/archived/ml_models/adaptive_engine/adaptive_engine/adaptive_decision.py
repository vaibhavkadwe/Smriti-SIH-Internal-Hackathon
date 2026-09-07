from typing import List, Optional, Tuple

from .models import (
    GamePerformance,
    BaselineData,
    DifficultyDecision,
    DecisionType,
    PerformanceTrend,
    MIN_DIFFICULTY,
    MAX_DIFFICULTY,
    INCREASE_ACCURACY_THRESHOLD,
    DECREASE_ACCURACY_THRESHOLD,
    HIGH_MISTAKE_THRESHOLD,
    BASELINE_COGNITIVE_FIELDS,
)


def _avg(values: List[float]) -> float:
    return (sum(values) / len(values)) if values else 0.0


def _linear_trend(values: List[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    xs = list(range(n))
    x_mean = _avg(xs)
    y_mean = _avg(values)
    num = sum(((x - x_mean) * (y - y_mean)) for x, y in zip(xs, values))
    den = sum(((x - x_mean) ** 2) for x in xs)
    return (num / den) if (den != 0) else 0.0


def _classify_trend(
    accuracy_trend: float,
    mistake_trend: float,
    rt_trend: float,
    ct_trend: float,
) -> PerformanceTrend:
    improve_score = 0.0
    decline_score = 0.0

    if accuracy_trend > 0.8:
        improve_score += 2
    elif accuracy_trend > 0.2:
        improve_score += 1
    elif accuracy_trend < -0.8:
        decline_score += 2
    elif accuracy_trend < -0.2:
        decline_score += 1

    if mistake_trend < -0.3:
        improve_score += 1.5
    elif mistake_trend < -0.05:
        improve_score += 0.5
    elif mistake_trend > 0.3:
        decline_score += 1.5
    elif mistake_trend > 0.05:
        decline_score += 0.5

    if rt_trend < -0.05:
        improve_score += 1
    elif rt_trend < -0.01:
        improve_score += 0.5
    elif rt_trend > 0.05:
        decline_score += 1
    elif rt_trend > 0.01:
        decline_score += 0.5

    if ct_trend < -0.5:
        improve_score += 1
    elif ct_trend < -0.1:
        improve_score += 0.5
    elif ct_trend > 0.5:
        decline_score += 1
    elif ct_trend > 0.1:
        decline_score += 0.5

    net = improve_score - decline_score
    if net >= 2:
        return PerformanceTrend.IMPROVING
    if net <= -2:
        return PerformanceTrend.DECLINING
    return PerformanceTrend.STABLE


def _baseline_strength_factor(baseline: Optional[BaselineData]) -> float:
    if baseline is None:
        return 1.0
    values = [baseline.get_cognitive_value(a) for a in BASELINE_COGNITIVE_FIELDS]
    cognitive_avg = sum(values) / len(values)
    if cognitive_avg >= 75:
        return 1.1
    if cognitive_avg >= 55:
        return 1.0
    return 0.9


def _make_reason(
    decision: DecisionType,
    avg_accuracy: float,
    avg_mistakes: float,
    trend: PerformanceTrend,
    current_difficulty: int,
    increase_count: int,
    decrease_count: int,
) -> str:
    if decision == DecisionType.INCREASE:
        reasons = []
        if avg_accuracy >= INCREASE_ACCURACY_THRESHOLD:
            reasons.append("consistently high accuracy")
        if avg_mistakes <= 2:
            reasons.append("low mistake count")
        if trend == PerformanceTrend.IMPROVING:
            reasons.append("clear improving trend across recent sessions")
        if (current_difficulty >= 2) and (increase_count >= 2):
            reasons.append("performing well at current difficulty")
        return (" and ".join(reasons)) if reasons else "overall performance warrants an increase"

    if decision == DecisionType.DECREASE:
        reasons = []
        if avg_accuracy <= DECREASE_ACCURACY_THRESHOLD:
            reasons.append("consistently low accuracy")
        if avg_mistakes >= HIGH_MISTAKE_THRESHOLD:
            reasons.append("frequent mistakes")
        if trend == PerformanceTrend.DECLINING:
            reasons.append("declining performance across recent sessions")
        if (current_difficulty <= 4) and (decrease_count >= 2):
            reasons.append("struggling at current difficulty")
        return (" and ".join(reasons)) if reasons else "overall performance warrants a decrease"

    if trend == PerformanceTrend.IMPROVING:
        return "improving but not yet ready for harder difficulty"
    if trend == PerformanceTrend.DECLINING:
        return "declining but not sharply enough to reduce difficulty"
    return "performance stable at current difficulty level"


def decide_next_difficulty(
    recent_sessions: List[GamePerformance],
    baseline: Optional[BaselineData] = None,
) -> DifficultyDecision:
    if not recent_sessions:
        current_diff = MIN_DIFFICULTY
    else:
        latest = recent_sessions[-1]
        current_diff = latest.current_difficulty

    n = len(recent_sessions)
    if n == 0:
        return DifficultyDecision(
            decision=DecisionType.MAINTAIN,
            current_difficulty=current_diff,
            recommended_difficulty=current_diff,
            performance_trend=PerformanceTrend.INSUFFICIENT_DATA,
            reason="no session history available to adapt difficulty",
        )

    if n == 1:
        perf = recent_sessions[0]
        if perf.accuracy >= INCREASE_ACCURACY_THRESHOLD:
            decision = DecisionType.MAINTAIN
            trend = PerformanceTrend.INSUFFICIENT_DATA
            reason = "single strong session; need more history before increasing"
        elif perf.accuracy <= DECREASE_ACCURACY_THRESHOLD:
            decision = DecisionType.DECREASE
            trend = PerformanceTrend.INSUFFICIENT_DATA
            reason = "single very weak session; reducing difficulty slightly"
        else:
            decision = DecisionType.MAINTAIN
            trend = PerformanceTrend.INSUFFICIENT_DATA
            reason = "only one session recorded; need more history for adaptation"
        recommended = _apply_decision(current_diff, decision)
        return DifficultyDecision(
            decision=decision,
            current_difficulty=current_diff,
            recommended_difficulty=recommended,
            performance_trend=trend,
            reason=reason,
        )

    accuracies = [s.accuracy for s in recent_sessions]
    mistakes = [float(s.mistakes) for s in recent_sessions]
    reaction_times = [s.reaction_time for s in recent_sessions]
    completion_times = [s.completion_time for s in recent_sessions]

    avg_accuracy = _avg(accuracies)
    avg_mistakes = _avg(mistakes)
    _unused_avg_reaction_time = _avg(reaction_times)

    accuracy_trend = _linear_trend(accuracies)
    mistake_trend = _linear_trend(mistakes)
    rt_trend = _linear_trend(reaction_times)
    ct_trend = _linear_trend(completion_times)

    trend = _classify_trend(accuracy_trend, mistake_trend, rt_trend, ct_trend)

    baseline_factor = _baseline_strength_factor(baseline)
    effective_increase_threshold = INCREASE_ACCURACY_THRESHOLD / baseline_factor
    effective_decrease_threshold = DECREASE_ACCURACY_THRESHOLD / baseline_factor

    increase_count = sum(1 for a in accuracies if (a >= effective_increase_threshold))
    decrease_count = sum(1 for a in accuracies if (a <= effective_decrease_threshold))

    decision = DecisionType.MAINTAIN
    need_increase_votes = (2 if (n >= 3) else 1)
    need_decrease_votes = (2 if (n >= 3) else 1)

    increase_condition = (
        (increase_count >= need_increase_votes)
        and (avg_accuracy >= effective_increase_threshold)
        and (avg_mistakes <= 3)
        and (trend != PerformanceTrend.DECLINING)
    )

    decrease_condition = (
        (
            (decrease_count >= need_decrease_votes)
            and (avg_accuracy <= effective_decrease_threshold)
        )
        or (
            (avg_mistakes >= HIGH_MISTAKE_THRESHOLD)
            and (decrease_count >= 1)
        )
    )

    borderline_increase = (
        (trend == PerformanceTrend.IMPROVING)
        and (avg_accuracy >= (INCREASE_ACCURACY_THRESHOLD - 5))
        and (increase_count >= (need_increase_votes - 1))
        and (current_diff < MAX_DIFFICULTY)
    )

    borderline_decrease = (
        (trend == PerformanceTrend.DECLINING)
        and (avg_accuracy <= (DECREASE_ACCURACY_THRESHOLD + 5))
        and (decrease_count >= (need_decrease_votes - 1))
        and (current_diff > MIN_DIFFICULTY)
    )

    if increase_condition:
        decision = DecisionType.INCREASE
    elif decrease_condition:
        decision = DecisionType.DECREASE
    elif borderline_increase:
        decision = DecisionType.INCREASE
    elif borderline_decrease:
        decision = DecisionType.DECREASE

    if (decision == DecisionType.INCREASE) and (current_diff == MAX_DIFFICULTY):
        decision = DecisionType.MAINTAIN
        reason_override = "already at maximum difficulty; maintain and consolidate"
        safe_trend = trend if (trend != PerformanceTrend.INSUFFICIENT_DATA) else PerformanceTrend.STABLE
        return DifficultyDecision(
            decision=decision,
            current_difficulty=current_diff,
            recommended_difficulty=MAX_DIFFICULTY,
            performance_trend=safe_trend,
            reason=reason_override,
        )

    if (decision == DecisionType.DECREASE) and (current_diff == MIN_DIFFICULTY):
        decision = DecisionType.MAINTAIN
        reason_override = "already at minimum difficulty; maintain with extra support"
        safe_trend = trend if (trend != PerformanceTrend.INSUFFICIENT_DATA) else PerformanceTrend.STABLE
        return DifficultyDecision(
            decision=decision,
            current_difficulty=current_diff,
            recommended_difficulty=MIN_DIFFICULTY,
            performance_trend=safe_trend,
            reason=reason_override,
        )

    recommended = _apply_decision(current_diff, decision)
    reason = _make_reason(
        decision,
        avg_accuracy,
        avg_mistakes,
        trend,
        current_diff,
        increase_count,
        decrease_count,
    )

    return DifficultyDecision(
        decision=decision,
        current_difficulty=current_diff,
        recommended_difficulty=recommended,
        performance_trend=trend,
        reason=reason,
    )


def _apply_decision(current: int, decision: DecisionType) -> int:
    if decision == DecisionType.INCREASE:
        candidate = current + 1
    elif decision == DecisionType.DECREASE:
        candidate = current - 1
    else:
        candidate = current
    return max(MIN_DIFFICULTY, min(MAX_DIFFICULTY, candidate))
