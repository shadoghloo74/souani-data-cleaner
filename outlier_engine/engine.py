"""OutlierEngine Orchestrator module."""

from typing import Dict, List, Optional, Union
import pandas as pd

from outlier_engine.services import DetectionService, TreatmentService
from outlier_engine.types import (
    DetectionMethod,
    DetectionResult,
    OutlierTreatmentAction,
    OutlierEngineConfig,
    OutlierEngineSummary,
    ColumnOutlierResult,
)


class OutlierEngine:
    """Orchestrator engine for detecting and treating outliers in pandas DataFrames."""

    def __init__(self, config: Optional[OutlierEngineConfig] = None):
        self.config = config or OutlierEngineConfig()

    def process(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: Union[str, DetectionMethod] = DetectionMethod.IQR,
        action: Union[str,
                      OutlierTreatmentAction] = OutlierTreatmentAction.CLIP,
        **kwargs,
    ) -> OutlierEngineSummary:
        """
        Process specified columns in a DataFrame through detection and treatment pipelines.
        """
        method_str = method.value if isinstance(
            method, DetectionMethod) else method
        action_str = action.value if isinstance(
            action, OutlierTreatmentAction) else action

        target_cols = columns or df.select_dtypes(
            include=["number"]).columns.tolist()
        processed_df = df.copy()
        col_results: Dict[str, ColumnOutlierResult] = {}

        total_outliers = 0

        for col in target_cols:
            if col not in df.columns:
                continue

            # 1. Delegate detection
            det_result: DetectionResult = DetectionService.detect_column(
                series=df[col], column_name=col, method=method_str, **kwargs
            )

            # 2. Delegate treatment
            treated_series: pd.Series = TreatmentService.treat_column(
                series=df[col], detection_result=det_result, action=action_str, **kwargs
            )

            processed_df[col] = treated_series
            total_outliers += det_result.outlier_count

            col_results[col] = ColumnOutlierResult(
                column_name=col,
                detection_result=det_result,
                treatment_action=action_str,
                modified_series=treated_series,
            )

        return OutlierEngineSummary(
            processed_df=processed_df,
            column_results=col_results,
            total_outliers_detected=total_outliers,
            execution_config=self.config,
        )
