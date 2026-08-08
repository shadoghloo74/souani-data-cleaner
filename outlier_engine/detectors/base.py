"""Base detector strategy module."""

from abc import ABC, abstractmethod
import pandas as pd
from outlier_engine.types import DetectionResult
from outlier_engine.exceptions import OutlierEngineError


def validate_numeric_column(series: pd.Series, column_name: str) -> None:
    """Validate that the target column is numeric."""
    if not pd.api.types.is_numeric_dtype(series):
        raise OutlierEngineError(f"Column '{column_name}' must be numeric for outlier detection.")


class BaseDetector(ABC):
    """Abstract Base Class for all outlier detection strategies."""

    @abstractmethod
    def detect(self, series: pd.Series, **kwargs) -> DetectionResult:
        """Execute detection on a pandas Series."""
        pass
