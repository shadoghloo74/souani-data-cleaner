"""JSON Exporter module for Outlier Engine reports."""

import json
from typing import Dict
from outlier_engine.models import (
    EngineReport,
    ExecutionContext,
    ColumnSummary,
    MetadataReport,
)


class JSONExporter:
    """Exporter responsible for serializing and deserializing EngineReport to/from JSON."""

    @staticmethod
    def export_to_string(report: EngineReport, indent: int = 2) -> str:
        """Export EngineReport to a JSON string."""
        return json.dumps(report.to_dict(), indent=indent)

    @staticmethod
    def export_to_file(report: EngineReport, file_path: str, indent: int = 2) -> None:
        """Export EngineReport directly to a JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=indent)

    @staticmethod
    def import_from_string(json_str: str) -> EngineReport:
        """Reconstruct EngineReport from a JSON string."""
        data = json.loads(json_str)
        ctx_data = data["context"]
        context = ExecutionContext(
            execution_id=ctx_data["execution_id"],
            timestamp=ctx_data["timestamp"],
            strict_numeric=ctx_data.get("strict_numeric", True),
            inplace=ctx_data.get("inplace", False),
            parameters=ctx_data.get("parameters", {}),
        )

        col_summaries: Dict[str, ColumnSummary] = {}
        for col, s in data["column_summaries"].items():
            col_summaries[col] = ColumnSummary(
                column_name=s["column_name"],
                detection_method=s["detection_method"],
                treatment_action=s["treatment_action"],
                outliers_detected=s["outliers_detected"],
                lower_bound=s.get("lower_bound"),
                upper_bound=s.get("upper_bound"),
                statistics=s.get("statistics", {}),
            )

        meta_data = data["metadata"]
        metadata = MetadataReport(
            total_rows=meta_data["total_rows"],
            total_columns=meta_data["total_columns"],
            processed_columns=meta_data["processed_columns"],
            numeric_columns=meta_data["numeric_columns"],
            missing_values_count=meta_data.get("missing_values_count", {}),
        )

        return EngineReport(
            context=context,
            column_summaries=col_summaries,
            metadata=metadata,
            total_outliers_detected=data["total_outliers_detected"],
            success=data.get("success", True),
        )
