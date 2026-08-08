"""Detection service module."""

import pandas as pd
from outlier_engine.registries import DetectionRegistry
from outlier_engine.types import DetectionResult
from outlier_engine.validators import ColumnValidator


class DetectionService:
    """Service responsible for executing detection via registered strategies."""

    @staticmethod
    def detect_column(series: pd.Series, column_name: str, method: str, **kwargs) -> DetectionResult:
        ColumnValidator.validate_numeric(series, column_name)
        detector = DetectionRegistry.get(method)
        return detector.detect(series, **kwargs)
