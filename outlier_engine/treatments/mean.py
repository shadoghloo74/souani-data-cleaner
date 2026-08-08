"""Mean replacement outlier treatment strategy."""

import pandas as pd
from outlier_engine.treatments.base import BaseTreatment
from outlier_engine.types import DetectionResult


class MeanTreatment(BaseTreatment):
    """Replaces outliers with the column mean."""

    def apply(self, series: pd.Series, detection_result: DetectionResult, **kwargs) -> pd.Series:
        treated = series.copy()
        clean = series[~detection_result.mask]
        fill_val = clean.mean() if not clean.empty else series.mean()
        treated[detection_result.mask] = fill_val
        return treated
