"""Clip outlier treatment strategy."""

import pandas as pd
from outlier_engine.treatments.base import BaseTreatment
from outlier_engine.types import DetectionResult


class ClipTreatment(BaseTreatment):
    """Clips outlier values to the upper and lower threshold bounds."""

    def apply(self, series: pd.Series, detection_result: DetectionResult, **kwargs) -> pd.Series:
        if detection_result.lower_bound is None or detection_result.upper_bound is None:
            return series.copy()
        return series.clip(lower=detection_result.lower_bound, upper=detection_result.upper_bound)
