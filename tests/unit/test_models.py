import pytest
import pandas as pd
from dataclasses import FrozenInstanceError

from outlier_engine.models import (
    DetectionResultModel,
    ColumnSummary,
    ExecutionContext,
    MetadataReport,
    EngineReport,
)


def test_detection_result_model():
    mask = pd.Series([False, True, False])
    model = DetectionResultModel(
        mask=mask,
        lower_bound=10.0,
        upper_bound=50.0,
        method="iqr",
        outlier_count=1,
        statistics={"q1": 15.0, "q3": 45.0},
    )

    # 1. Verification of properties & types
    assert model.method == "iqr"
    assert model.outlier_count == 1
    assert model.lower_bound == 10.0

    # 2. Immutability test
    with pytest.raises(FrozenInstanceError):
        model.outlier_count = 5  # type: ignore

    # 3. Serialization
    serialized = model.to_dict()
    assert isinstance(serialized, dict)
    assert serialized["mask"] == [False, True, False]
    assert serialized["method"] == "iqr"


def test_column_summary_model():
    col1 = ColumnSummary("age", "iqr", "clip", 2, 0.0, 100.0, {"median": 30.0})
    col2 = ColumnSummary("age", "iqr", "clip", 2, 0.0, 100.0, {"median": 30.0})

    # Equality & Immutability
    assert col1 == col2
    with pytest.raises(FrozenInstanceError):
        col1.column_name = "height"  # type: ignore

    # Serialization
    serialized = col1.to_dict()
    assert serialized["column_name"] == "age"


def test_execution_context_model():
    context = ExecutionContext("exec-123", "2026-08-07T20:00:00", True, False, {"multiplier": 1.5})
    assert context.execution_id == "exec-123"

    with pytest.raises(FrozenInstanceError):
        context.inplace = True  # type: ignore

    assert context.to_dict()["parameters"]["multiplier"] == 1.5


def test_metadata_report_model():
    metadata = MetadataReport(100, 3, ["col1", "col2"], ["col1", "col2"], {"col1": 0})
    assert metadata.total_rows == 100

    with pytest.raises(FrozenInstanceError):
        metadata.total_rows = 200  # type: ignore


def test_engine_report_model():
    ctx = ExecutionContext("exec-1", "2026-08-07", True, False)
    meta = MetadataReport(10, 1, ["col1"], ["col1"], {})
    col_sum = ColumnSummary("col1", "iqr", "clip", 1, 0.0, 10.0)

    report = EngineReport(
        context=ctx,
        column_summaries={"col1": col_sum},
        metadata=meta,
        total_outliers_detected=1,
        success=True,
    )

    assert report.total_outliers_detected == 1
    with pytest.raises(FrozenInstanceError):
        report.success = False  # type: ignore

    serialized = report.to_dict()
    assert serialized["context"]["execution_id"] == "exec-1"
    assert serialized["column_summaries"]["col1"]["column_name"] == "col1"
