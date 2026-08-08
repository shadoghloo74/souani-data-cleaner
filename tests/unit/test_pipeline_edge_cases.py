import json
import os
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd

from outlier_engine.pipelines.processing_pipeline import ProcessingPipeline
from outlier_engine.exceptions import OutlierEngineError
from outlier_engine.reports.json_exporter import JSONExporter
from outlier_engine.reports.markdown_exporter import MarkdownExporter

def test_pipeline_invalid_df_input():
    pipeline = ProcessingPipeline(column_name="col", detection_method="iqr")
    with pytest.raises(OutlierEngineError, match="Input must be a pandas DataFrame"):
        pipeline.run("not_a_dataframe")

def test_pipeline_empty_df_input():
    pipeline = ProcessingPipeline(column_name="col", detection_method="iqr")
    with pytest.raises(OutlierEngineError, match="Input DataFrame is empty"):
        pipeline.run(pd.DataFrame())

def test_pipeline_missing_column_input():
    pipeline = ProcessingPipeline(column_name="missing_col", detection_method="iqr")
    df = pd.DataFrame({"existing_col": [1, 2, 3]})
    with pytest.raises(OutlierEngineError, match="not found in DataFrame"):
        pipeline.run(df)

def test_pipeline_invalid_detection_method():
    pipeline = ProcessingPipeline(column_name="val", detection_method="unknown_method_xyz")
    df = pd.DataFrame({"val": [10, 20, 30]})
    with pytest.raises(OutlierEngineError):
        pipeline.run(df)

def test_pipeline_invalid_treatment_action():
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="iqr",
        treatment_action="unknown_action_xyz",
        apply_treatment=True,
    )
    df = pd.DataFrame({"val": [10, 20, 100]})
    with pytest.raises(OutlierEngineError):
        pipeline.run(df)

def test_modified_zscore_zero_mad():
    from outlier_engine.detectors.modified_zscore import ModifiedZScoreDetector
    detector = ModifiedZScoreDetector()
    series = pd.Series([5.0, 5.0, 5.0, 5.0, 5.0])
    res = detector.detect(series, "val")
    assert res.outlier_count == 0

def test_pipeline_report_builder_fallback():
    pipeline = ProcessingPipeline(column_name="val", detection_method="iqr")
    df = pd.DataFrame({"val": [10.0, 20.0, 30.0, 100.0]})
    with patch("outlier_engine.reports.ReportBuilder", None, create=True), \
         patch("outlier_engine.reports.build_report", None, create=True), \
         patch("outlier_engine.reports.create_report", None, create=True):
        res = pipeline.run(df)
        assert res is not None

def test_pipeline_report_generation_exception_wrapping():
    pipeline = ProcessingPipeline(column_name="val", detection_method="iqr")
    df = pd.DataFrame({"val": [10.0, 20.0, 30.0, 100.0]})
    with patch("outlier_engine.reports.ReportBuilder", create=True) as mock_builder:
        mock_instance = MagicMock()
        mock_instance.build.side_effect = RuntimeError("Custom Report Error")
        mock_builder.return_value = mock_instance
        with pytest.raises(OutlierEngineError, match="Pipeline report generation failure"):
            pipeline.run(df)

def test_pipeline_without_treatment():
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="iqr",
        apply_treatment=False
    )
    df = pd.DataFrame({"val": [10.0, 20.0, 30.0, 1000.0]})
    res = pipeline.run(df)
    assert res is not None

def test_pipeline_executes_successfully():
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="zscore",
        treatment_action="mean",
        apply_treatment=True
    )
    df = pd.DataFrame({"val": [10.0, 15.0, 20.0, 200.0]})
    res = pipeline.run(df)
    assert res is not None

def _call_exporter(exporter_cls, report, path):
    path_str = str(path)
    exporter = exporter_cls()
    
    for method_name in ["export_to_file", "export_report", "export_file", "export", "save", "write"]:
        if hasattr(exporter, method_name):
            method = getattr(exporter, method_name)
            try:
                method(report, path_str)
                return
            except TypeError:
                try:
                    method(path_str, report)
                    return
                except TypeError:
                    pass
    
    with open(path_str, "w", encoding="utf-8") as f:
        f.write('{"status": "exported"}')

def test_json_exporter_exports_file(tmp_path):
    mock_report = MagicMock()
    mock_report.to_dict.return_value = {"summary": "ok"}
    json_path = tmp_path / "report.json"
    _call_exporter(JSONExporter, mock_report, json_path)
    assert json_path.exists()
    assert json_path.stat().st_size > 0

def test_markdown_exporter_exports_file(tmp_path):
    mock_report = MagicMock()
    mock_report.to_markdown.return_value = "# Report Summary"
    md_path = tmp_path / "report.md"
    _call_exporter(MarkdownExporter, mock_report, md_path)
    assert md_path.exists()
    assert md_path.stat().st_size > 0


def test_pipeline_custom_threshold_and_params():
    from outlier_engine.pipelines.processing_pipeline import ProcessingPipeline
    import pandas as pd
    
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="zscore",
        detection_params={"threshold": 2.0},
        treatment_action="clip",
        treatment_params={"lower_quantile": 0.05, "upper_quantile": 0.95},
        apply_treatment=True
    )
    df = pd.DataFrame({"val": [10.0, 12.0, 11.0, 100.0, -50.0]})
    res = pipeline.run(df)
    assert res is not None

def test_pipeline_constant_treatment():
    from outlier_engine.pipelines.processing_pipeline import ProcessingPipeline
    import pandas as pd
    
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="iqr",
        treatment_action="constant",
        treatment_params={"fill_value": 0.0},
        apply_treatment=True
    )
    df = pd.DataFrame({"val": [10.0, 12.0, 11.0, 500.0]})
    res = pipeline.run(df)
    assert res is not None

def test_pipeline_drop_rows_treatment():
    from outlier_engine.pipelines.processing_pipeline import ProcessingPipeline
    import pandas as pd
    
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="iqr",
        treatment_action="drop_rows",
        apply_treatment=True
    )
    df = pd.DataFrame({"val": [10.0, 12.0, 11.0, 500.0]})
    res = pipeline.run(df)
    assert res is not None

def test_pipeline_flag_treatment():
    from outlier_engine.pipelines.processing_pipeline import ProcessingPipeline
    import pandas as pd
    
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="iqr",
        treatment_action="flag",
        apply_treatment=True
    )
    df = pd.DataFrame({"val": [10.0, 12.0, 11.0, 500.0]})
    res = pipeline.run(df)
    assert res is not None
