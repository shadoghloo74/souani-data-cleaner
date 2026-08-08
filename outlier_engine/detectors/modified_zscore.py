"""Modified Z-score outlier detector strategy (robust to extreme outliers)."""

import pandas as pd
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.types import DetectionMethod, DetectionResult


class ModifiedZScoreDetector(BaseDetector):
    """Detector for identifying outliers using Modified Z-score based on MAD."""

    def detect(self, series: pd.Series, threshold: float = 3.5, **kwargs) -> DetectionResult:
        clean_series = series.dropna()

        if clean_series.empty:
            mask = pd.Series(False, index=series.index)
            return DetectionResult(
                mask=mask,
                lower_bound=None,
                upper_bound=None,
                method=DetectionMethod.MODIFIED_ZSCORE,
                outlier_count=0,
                statistics={"median": None, "mad": None},
            )

        median = float(clean_series.median())
        mad = float((clean_series - median).abs().median())

        if mad == 0:
            mask = pd.Series(False, index=series.index)
            return DetectionResult(
                mask=mask,
                lower_bound=median,
                upper_bound=median,
                method=DetectionMethod.MODIFIED_ZSCORE,
                outlier_count=0,
                statistics={"median": median, "mad": 0.0},
            )

        mod_z = 0.6745 * (series - median).abs() / mad
        mask = mod_z > threshold
        mask = mask.fillna(False)

        lower_bound = float(median - (threshold * mad / 0.6745))
        upper_bound = float(median + (threshold * mad / 0.6745))

        return DetectionResult(
            mask=mask,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            method=DetectionMethod.MODIFIED_ZSCORE,
            outlier_count=int(mask.sum()),
            statistics={"median": median, "mad": mad, "threshold": threshold},
        )
