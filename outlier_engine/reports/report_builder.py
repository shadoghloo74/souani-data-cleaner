"""Report builder module for Outlier Engine."""

import pandas as pd
from typing import Dict, List, Optional
from outlier_engine.models import (
    EngineReport,
    ExecutionContext,
    ColumnSummary,
    MetadataReport,
    DetectionResultModel,
)


class ReportBuilder:
    """Builder class for constructing an EngineReport using existing Data Models."""

    def __init__(self, execution_context: ExecutionContext):
        self._context = execution_context
        self._column_summaries: Dict[str, ColumnSummary] = {}
        self._total_outliers = 0
        self._metadata: Optional[MetadataReport] = None

    def capture_metadata(
        self,
        df_before: pd.DataFrame,
        processed_columns: List[str],
    ) -> "ReportBuilder":
        """Capture metadata from input dataframe before processing."""
        numeric_cols = df_before.select_dtypes(
            include=["number"]).columns.tolist()
        missing_counts = df_before[processed_columns].isnull().sum().to_dict()

        self._metadata = MetadataReport(
            total_rows=len(df_before),
            total_columns=len(df_before.columns),
            processed_columns=processed_columns,
            numeric_columns=numeric_cols,
            missing_values_count=missing_counts,
        )
        return self

    def add_column_summary(
        self,
        column_name: str,
        detection_method: str,
        treatment_action: str,
        detection_result: DetectionResultModel,
    ) -> "ReportBuilder":
        """Add column summary using a DetectionResultModel."""
        summary = ColumnSummary(
            column_name=column_name,
            detection_method=detection_method,
            treatment_action=treatment_action,
            outliers_detected=detection_result.outlier_count,
            lower_bound=detection_result.lower_bound,
            upper_bound=detection_result.upper_bound,
            statistics=detection_result.statistics,
        )
        self._column_summaries[column_name] = summary
        self._total_outliers += detection_result.outlier_count
        return self

    def build(self) -> EngineReport:
        """Construct the final immutable EngineReport object."""
        if self._metadata is None:
            self._metadata = MetadataReport(
                total_rows=0,
                total_columns=0,
                processed_columns=list(self._column_summaries.keys()),
                numeric_columns=[],
                missing_values_count={},
            )

        return EngineReport(
            context=self._context,
            column_summaries=self._column_summaries,
            metadata=self._metadata,
            total_outliers_detected=self._total_outliers,
            success=True,
        )
