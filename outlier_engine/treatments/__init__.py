"""Treatments module initialization for Outlier Engine."""

from outlier_engine.treatments.base import BaseTreatment
from outlier_engine.treatments.clip import ClipTreatment
from outlier_engine.treatments.mean import MeanTreatment
from outlier_engine.treatments.median import MedianTreatment
from outlier_engine.treatments.constant import ConstantTreatment
from outlier_engine.treatments.drop_rows import DropRowsTreatment
from outlier_engine.treatments.flag import FlagTreatment

__all__ = [
    "BaseTreatment",
    "ClipTreatment",
    "MeanTreatment",
    "MedianTreatment",
    "ConstantTreatment",
    "DropRowsTreatment",
    "FlagTreatment",
]
