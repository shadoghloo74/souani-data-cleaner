"""Percentile-based outlier detector strategy."""

import pandas as pd
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.types import DetectionMethod, DetectionResult


class PercentileDetector(BaseDetector):
    """Detector for identifying outliers outside percentile bounds."""

    def detect(
        self, series: pd.Series, lower_quantile: float = 0.01, upper_quantile: float = 0.99, **kwargs
    ) -> DetectionResult:
        clean_series = series.dropna()

        if clean_series.empty:
            mask = pd.Series(False, index=series.index)
            return DetectionResult(
                mask=mask,
                lower_bound=None,
                upper_bound=None,
                method=DetectionMethod.PERCENTILE,
                outlier_count=0,
                statistics={"lower_quantile": lower_quantile, "upper_quantile": upper_quantile},
            )

        lower_bound = float(clean_series.quantile(lower_quantile))
        upper_bound = float(clean_series.quantile(upper_quantile))

        mask = (series < lower_bound) | (series > upper_bound)
        mask = mask.fillna(False)

        return DetectionResult(
            mask=mask,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            method=DetectionMethod.PERCENTILE,
            outlier_count=int(mask.sum()),
            statistics={
                "lower_quantile": lower_quantile,
                "upper_quantile": upper_quantile,
            },
        )
