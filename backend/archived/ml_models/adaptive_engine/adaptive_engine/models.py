from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime, timezone


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DecisionType(str, Enum):
    INCREASE = "INCREASE_DIFFICULTY"
    MAINTAIN = "MAINTAIN_DIFFICULTY"
    DECREASE = "DECREASE_DIFFICULTY"


class PerformanceTrend(str, Enum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class CognitiveStatus(str, Enum):
    NORMAL = "normal"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


MIN_DIFFICULTY: int = 1
MAX_DIFFICULTY: int = 5
MIN_BASELINE_SCORE: int = 0
MAX_BASELINE_SCORE: int = 100

DEFAULT_MISSING_BASELINE: float = 50.0

COGNITIVE_STATUS_WEIGHTS: Dict[str, float] = {
    "normal": 1.0,
    "mild": 0.75,
    "moderate": 0.55,
    "severe": 0.35,
}

CONCERN_PENALTY: float = 0.08

STARTING_ACCURACY_THRESHOLD: float = 70.0
INCREASE_ACCURACY_THRESHOLD: float = 85.0
DECREASE_ACCURACY_THRESHOLD: float = 55.0
HIGH_MISTAKE_THRESHOLD: int = 5

BASELINE_COGNITIVE_FIELDS: List[str] = [
    "baseline_memory",
    "baseline_attention",
    "baseline_reasoning",
    "baseline_processing_speed",
]


@dataclass
class BaselineData:
    patient_id: str
    baseline_memory: Optional[float] = None
    baseline_attention: Optional[float] = None
    baseline_reasoning: Optional[float] = None
    baseline_processing_speed: Optional[float] = None
    baseline_reaction_time: Optional[float] = None

    def __post_init__(self) -> None:
        for attr in BASELINE_COGNITIVE_FIELDS:
            val = getattr(self, attr)
            if val is not None and not (MIN_BASELINE_SCORE <= val <= MAX_BASELINE_SCORE):
                raise ValueError(
                    f"{attr} must be between {MIN_BASELINE_SCORE} and {MAX_BASELINE_SCORE} when provided"
                )
        rt = getattr(self, "baseline_reaction_time")
        if rt is not None and rt <= 0:
            raise ValueError("baseline_reaction_time must be positive when provided")

    def get_cognitive_value(self, attr: str) -> float:
        val = getattr(self, attr)
        if val is not None:
            return float(val)
        return DEFAULT_MISSING_BASELINE

    def has_any_cognitive(self) -> bool:
        return any(getattr(self, a) is not None for a in BASELINE_COGNITIVE_FIELDS)

    def has_reaction_time(self) -> bool:
        return self.baseline_reaction_time is not None


@dataclass
class PatientReportData:
    cognitive_status: Optional[str] = None
    memory_concern: Optional[bool] = None
    attention_concern: Optional[bool] = None
    reasoning_concern: Optional[bool] = None

    def __post_init__(self) -> None:
        if self.cognitive_status is not None:
            valid_statuses = set(COGNITIVE_STATUS_WEIGHTS.keys())
            if self.cognitive_status not in valid_statuses:
                raise ValueError(
                    f"cognitive_status must be one of {sorted(valid_statuses)} or None"
                )


@dataclass
class GamePerformance:
    patient_id: str
    game_type: str
    current_difficulty: int
    accuracy: float
    mistakes: int
    reaction_time: float
    completion_time: float
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if not (MIN_DIFFICULTY <= self.current_difficulty <= MAX_DIFFICULTY):
            raise ValueError(
                f"current_difficulty must be between {MIN_DIFFICULTY} and {MAX_DIFFICULTY}"
            )
        if not (0 <= self.accuracy <= 100):
            raise ValueError("accuracy must be between 0 and 100")
        if self.mistakes < 0:
            raise ValueError("mistakes must be non-negative")
        if self.reaction_time <= 0:
            raise ValueError("reaction_time must be positive")
        if self.completion_time <= 0:
            raise ValueError("completion_time must be positive")


@dataclass
class DifficultyDecision:
    decision: DecisionType
    current_difficulty: int
    recommended_difficulty: int
    performance_trend: PerformanceTrend
    reason: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "decision": self.decision.value,
            "current_difficulty": self.current_difficulty,
            "recommended_difficulty": self.recommended_difficulty,
            "performance_trend": self.performance_trend.value,
            "reason": self.reason,
        }
