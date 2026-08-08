"""Registries module initialization and default strategy registration."""

from outlier_engine.registries.detection_registry import DetectionRegistry
from outlier_engine.registries.treatment_registry import TreatmentRegistry
from outlier_engine.detectors import (
    IQRDetector, ZScoreDetector, ModifiedZScoreDetector, PercentileDetector, StdDevDetector
)
from outlier_engine.treatments import (
    ClipTreatment, MeanTreatment, MedianTreatment, ConstantTreatment, DropRowsTreatment, FlagTreatment
)

DetectionRegistry.register("iqr", IQRDetector)
DetectionRegistry.register("zscore", ZScoreDetector)
DetectionRegistry.register("modified_zscore", ModifiedZScoreDetector)
DetectionRegistry.register("percentile", PercentileDetector)
DetectionRegistry.register("std_dev", StdDevDetector)

TreatmentRegistry.register("clip", ClipTreatment)
TreatmentRegistry.register("mean", MeanTreatment)
TreatmentRegistry.register("median", MedianTreatment)
TreatmentRegistry.register("constant", ConstantTreatment)
TreatmentRegistry.register("drop_rows", DropRowsTreatment)
TreatmentRegistry.register("flag", FlagTreatment)

__all__ = ["DetectionRegistry", "TreatmentRegistry"]
