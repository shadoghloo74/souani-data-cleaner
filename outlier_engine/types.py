"""Type definitions and data models for Outlier Engine."""

from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
import pandas as pd


class DetectionMethod(str, Enum):
    IQR = "iqr"
    ZSCORE = "zscore"
    MODIFIED_ZSCORE = "modified_zscore"
    PERCENTILE = "percentile"
    STD_DEV = "std_dev"


class OutlierTreatmentAction(str, Enum):
    CLIP = "clip"
    MEAN = "mean"
    MEDIAN = "median"
    CONSTANT = "constant"
    DROP_ROWS = "drop_rows"
    FLAG = "flag"


@dataclass
class DetectionResult:
    mask: pd.Series
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    method: DetectionMethod
    outlier_count: int
    statistics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ColumnOutlierResult:
    column_name: str
    detection_result: DetectionResult
    treatment_action: str
    modified_series: pd.Series


@dataclass
class OutlierEngineConfig:
    strict_numeric: bool = True
    inplace: bool = False


@dataclass
class OutlierEngineSummary:
    processed_df: pd.DataFrame
    column_results: Dict[str, ColumnOutlierResult]
    total_outliers_detected: int
    execution_config: OutlierEngineConfig
