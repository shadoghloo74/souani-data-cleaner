import pytest
import pandas as pd
from outlier_engine.models import ExecutionContext, DetectionResultModel
from outlier_engine.reports import ReportBuilder, JSONExporter, MarkdownExporter


def test_report_builder_and_exporters():
    ctx = ExecutionContext("exec-99", "2026-08-07T21:00:00", True, False)
    builder = ReportBuilder(ctx)

    df = pd.DataFrame({"col1": [1.0, 2.0, 100.0], "col2": [5, 6, 7]})
    builder.capture_metadata(df, ["col1"])

    det_res = DetectionResultModel(
        mask=pd.Series([False, False, True]),
        lower_bound=-1.0,
        upper_bound=10.0,
        method="iqr",
        outlier_count=1,
        statistics={"q1": 1.0, "q3": 2.0},
    )

    builder.add_column_summary("col1", "iqr", "clip", det_res)
    report = builder.build()

    assert report.total_outliers_detected == 1
    assert "col1" in report.column_summaries
    assert report.metadata.total_rows == 3

    # Test JSON Exporter (String)
    json_str = JSONExporter.export_to_string(report)
    assert "exec-99" in json_str
    assert "col1" in json_str

    # Test JSON Import
    imported_report = JSONExporter.import_from_string(json_str)
    assert imported_report.context.execution_id == "exec-99"
    assert imported_report.total_outliers_detected == 1
    assert imported_report.column_summaries["col1"].outliers_detected == 1

    # Test Markdown Exporter
    md = MarkdownExporter.export(report)
    assert "# Outlier Engine Execution Report" in md
    assert "exec-99" in md
    assert "col1" in md
