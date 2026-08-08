"""Detection result data model."""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional
import pandas as pd


@dataclass(frozen=True)
class DetectionResultModel:
    """Data model representing the output of an outlier detection strategy."""

    mask: pd.Series
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    method: str
    outlier_count: int
    statistics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize data model to dictionary."""
        data = asdict(self)
        data["mask"] = self.mask.to_list()
        return data
