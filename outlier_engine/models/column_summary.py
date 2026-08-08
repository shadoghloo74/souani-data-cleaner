"""Column summary data model."""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ColumnSummary:
    """Data model summarizing detection and treatment results for a single column."""

    column_name: str
    detection_method: str
    treatment_action: str
    outliers_detected: int
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    statistics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize data model to dictionary."""
        return asdict(self)
