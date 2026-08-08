"""Engine report data model."""

from dataclasses import dataclass
from typing import Any, Dict
from outlier_engine.models.execution_context import ExecutionContext
from outlier_engine.models.column_summary import ColumnSummary
from outlier_engine.models.metadata_report import MetadataReport


@dataclass(frozen=True)
class EngineReport:
    """Data model representing the complete summary report of OutlierEngine."""

    context: ExecutionContext
    column_summaries: Dict[str, ColumnSummary]
    metadata: MetadataReport
    total_outliers_detected: int
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize data model to dictionary."""
        return {
            "context": self.context.to_dict(),
            "column_summaries": {k: v.to_dict() for k, v in self.column_summaries.items()},
            "metadata": self.metadata.to_dict(),
            "total_outliers_detected": self.total_outliers_detected,
            "success": self.success,
        }
