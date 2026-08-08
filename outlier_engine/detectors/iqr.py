"""Interquartile Range (IQR) outlier detector strategy."""

import pandas as pd
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.types import DetectionMethod, DetectionResult


class IQRDetector(BaseDetector):
    """Detector for identifying outliers using the Interquartile Range (IQR) method."""

    def detect(self, series: pd.Series, multiplier: float = 1.5, **kwargs) -> DetectionResult:
        """
        Detect outliers in a pandas Series using IQR thresholds.

        Args:
            series (pd.Series): The target numeric column.
            multiplier (float): IQR multiplier factor (default 1.5).

        Returns:
            DetectionResult: Standardized detection output.
        """
        clean_series = series.dropna()

        if clean_series.empty:
            mask = pd.Series(False, index=series.index)
            return DetectionResult(
                mask=mask,
                lower_bound=None,
                upper_bound=None,
                method=DetectionMethod.IQR,
                outlier_count=0,
                statistics={"q1": None, "q3": None, "iqr": None},
            )

        q1 = float(clean_series.quantile(0.25))
        q3 = float(clean_series.quantile(0.75))
        iqr = q3 - q1

        lower_bound = float(q1 - multiplier * iqr)
        upper_bound = float(q3 + multiplier * iqr)

        mask = (series < lower_bound) | (series > upper_bound)
        mask = mask.fillna(False)

        return DetectionResult(
            mask=mask,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            method=DetectionMethod.IQR,
            outlier_count=int(mask.sum()),
            statistics={"q1": q1, "q3": q3, "iqr": iqr, "multiplier": multiplier},
        )
