import pytest
import pandas as pd
from outlier_engine.services import DetectionService, TreatmentService
from outlier_engine.models import ExecutionContext, DetectionResultModel
from outlier_engine.reports import ReportBuilder, JSONExporter, MarkdownExporter
from outlier_engine.metadata import ExecutionMetadata


def test_end_to_end_reporting_workflow():
    df = pd.DataFrame({
        "feature1": [10.0, 12.0, 11.0, 13.0, 100.0, -50.0],
        "feature2": [5.0, 6.0, 5.5, 6.2, 5.8, 6.1]
    })

    # 1. Run Detection & Treatment
    col = "feature1"
    det_res = DetectionService.detect_column(df[col], col, method="iqr", multiplier=1.5)
    treated_series = TreatmentService.treat_column(df[col], det_res, action="clip")

    # 2. Wrap Detection into Model
    model_det_res = DetectionResultModel(
        mask=det_res.mask,
        lower_bound=det_res.lower_bound,
        upper_bound=det_res.upper_bound,
        method=det_res.method.value if hasattr(det_res.method, 'value') else str(det_res.method),
        outlier_count=det_res.outlier_count,
        statistics=det_res.statistics
    )

    # 3. Build Metadata & Execution Context
    exec_meta = ExecutionMetadata(detector="iqr", treatment="clip", columns=[col])
    ctx = ExecutionContext(
        execution_id=exec_meta.execution_id,
        timestamp=exec_meta.timestamp,
        strict_numeric=True,
        inplace=False,
        parameters={"multiplier": 1.5}
    )

    # 4. Report Builder Workflow
    builder = ReportBuilder(ctx)
    builder.capture_metadata(df, [col])
    builder.add_column_summary(col, "iqr", "clip", model_det_res)
    engine_report = builder.build()

    # 5. Export Checks
    json_str = JSONExporter.export_to_string(engine_report)
    imported = JSONExporter.import_from_string(json_str)
    md_str = MarkdownExporter.export(engine_report)

    assert imported.context.execution_id == ctx.execution_id
    assert imported.total_outliers_detected == 2
    assert "feature1" in md_str
    assert "clip" in md_str
