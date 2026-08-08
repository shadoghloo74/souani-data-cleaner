"""Z-score outlier detector strategy."""

import pandas as pd
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.types import DetectionMethod, DetectionResult


class ZScoreDetector(BaseDetector):
    """Detector for identifying outliers using standard Z-score thresholding."""

    def detect(self, series: pd.Series, threshold: float = 3.0, **kwargs) -> DetectionResult:
        """
        Detect outliers using Z-score threshold.

        Args:
            series (pd.Series): The target numeric column.
            threshold (float): Z-score cutoff limit (default 3.0).

        Returns:
            DetectionResult: Standardized detection output.
        """
        clean_series = series.dropna()

        if clean_series.empty or clean_series.std() == 0:
            mask = pd.Series(False, index=series.index)
            return DetectionResult(
                mask=mask,
                lower_bound=None,
                upper_bound=None,
                method=DetectionMethod.ZSCORE,
                outlier_count=0,
                statistics={"mean": None, "std": None},
            )

        mean = float(clean_series.mean())
        std = float(clean_series.std())

        lower_bound = float(mean - threshold * std)
        upper_bound = float(mean + threshold * std)

        z_scores = (series - mean) / std
        mask = z_scores.abs() > threshold
        mask = mask.fillna(False)

        return DetectionResult(
            mask=mask,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            method=DetectionMethod.ZSCORE,
            outlier_count=int(mask.sum()),
            statistics={"mean": mean, "std": std, "threshold": threshold},
        )
