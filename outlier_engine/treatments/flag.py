"""Flag outlier treatment strategy."""

import pandas as pd
from outlier_engine.treatments.base import BaseTreatment
from outlier_engine.types import DetectionResult


class FlagTreatment(BaseTreatment):
    """Keeps original values intact without modifying data values."""

    def apply(self, series: pd.Series, detection_result: DetectionResult, **kwargs) -> pd.Series:
        return series.copy()
