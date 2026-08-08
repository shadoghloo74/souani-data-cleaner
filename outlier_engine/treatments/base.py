"""Base treatment strategy module."""

from abc import ABC, abstractmethod
import pandas as pd
from outlier_engine.types import DetectionResult


class BaseTreatment(ABC):
    """Abstract Base Class for all outlier treatment strategies."""

    @abstractmethod
    def apply(self, series: pd.Series, detection_result: DetectionResult, **kwargs) -> pd.Series:
        """Apply treatment to a pandas Series using DetectionResult."""
        pass
