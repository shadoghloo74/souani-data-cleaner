"""Detectors module initialization for Outlier Engine."""

from outlier_engine.detectors.base import BaseDetector
from outlier_engine.detectors.iqr import IQRDetector
from outlier_engine.detectors.zscore import ZScoreDetector
from outlier_engine.detectors.modified_zscore import ModifiedZScoreDetector
from outlier_engine.detectors.percentile import PercentileDetector
from outlier_engine.detectors.std_dev import StdDevDetector

__all__ = [
    "BaseDetector",
    "IQRDetector",
    "ZScoreDetector",
    "ModifiedZScoreDetector",
    "PercentileDetector",
    "StdDevDetector",
]
