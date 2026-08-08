"""Drop rows / NaN assignment outlier treatment strategy."""

import numpy as np
import pandas as pd
from outlier_engine.treatments.base import BaseTreatment
from outlier_engine.types import DetectionResult


class DropRowsTreatment(BaseTreatment):
    """Replaces outliers with NaN for downstream deletion."""

    def apply(self, series: pd.Series, detection_result: DetectionResult, **kwargs) -> pd.Series:
        treated = series.copy()
        treated[detection_result.mask] = np.nan
        return treated
