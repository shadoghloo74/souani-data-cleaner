"""Treatment service module."""

import pandas as pd
from outlier_engine.registries import TreatmentRegistry
from outlier_engine.types import DetectionResult


class TreatmentService:
    """Service responsible for executing treatment via registered strategies."""

    @staticmethod
    def treat_column(series: pd.Series, detection_result: DetectionResult, action: str, **kwargs) -> pd.Series:
        treatment = TreatmentRegistry.get(action)
        return treatment.apply(series, detection_result, **kwargs)
