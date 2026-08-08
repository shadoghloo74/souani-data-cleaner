"""Constant value replacement outlier treatment strategy."""

import pandas as pd
from outlier_engine.treatments.base import BaseTreatment
from outlier_engine.types import DetectionResult


class ConstantTreatment(BaseTreatment):
    """Replaces outliers with a specific constant value."""

    def apply(self, series: pd.Series, detection_result: DetectionResult, value: float = 0.0, **kwargs) -> pd.Series:
        treated = series.copy()
        fill_val = kwargs.get("fill_value", value)
        treated[detection_result.mask] = fill_val
        return treated
