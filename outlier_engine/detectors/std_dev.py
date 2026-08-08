"""Standard Deviation outlier detector strategy."""

import pandas as pd
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.types import DetectionMethod, DetectionResult


class StdDevDetector(BaseDetector):
    """Detector for identifying outliers outside N standard deviations."""

    def detect(self, series: pd.Series, n_std: float = 3.0, **kwargs) -> DetectionResult:
        clean_series = series.dropna()

        if clean_series.empty:
            mask = pd.Series(False, index=series.index)
            return DetectionResult(
                mask=mask,
                lower_bound=None,
                upper_bound=None,
                method=DetectionMethod.STD_DEV,
                outlier_count=0,
                statistics={"mean": None, "std": None},
            )

        mean = float(clean_series.mean())
        std = float(clean_series.std())

        lower_bound = float(mean - n_std * std)
        upper_bound = float(mean + n_std * std)

        mask = (series < lower_bound) | (series > upper_bound)
        mask = mask.fillna(False)

        return DetectionResult(
            mask=mask,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            method=DetectionMethod.STD_DEV,
            outlier_count=int(mask.sum()),
            statistics={"mean": mean, "std": std, "n_std": n_std},
        )
