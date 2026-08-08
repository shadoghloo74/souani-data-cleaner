import pytest
import pandas as pd

from outlier_engine.pipelines import ProcessingPipeline, PipelineResult
from outlier_engine.exceptions import OutlierEngineError


def test_pipeline_creation_valid():
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="zscore",
        treatment_action="median",
    )
    assert pipeline.column_name == "val"
    assert pipeline.detection_method == "zscore"
    assert pipeline.treatment_action == "median"


def test_pipeline_invalid_configuration():
    with pytest.raises(OutlierEngineError, match="Invalid column_name"):
        ProcessingPipeline(column_name="", detection_method="zscore")

    with pytest.raises(OutlierEngineError, match="Invalid detection_method"):
        ProcessingPipeline(column_name="val", detection_method="")


def test_pipeline_execution_without_treatment():
    df = pd.DataFrame({"val": [10.0, 12.0, 11.0, 100.0, 10.5]})
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="zscore",
        apply_treatment=False,
    )

    result = pipeline.run(df)
    assert isinstance(result, PipelineResult)
    assert result.detection_result is not None
    assert result.detection_result.outlier_count >= 1
    assert result.metadata.treatment_action is None
    # DataFrame remains unmodified
    pd.testing.assert_frame_equal(result.processed_df, df)


def test_pipeline_execution_with_detection_and_treatment():
    df = pd.DataFrame({"val": [10.0, 12.0, 11.0, 100.0, 10.5]})
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="zscore",
        treatment_action="median",
        apply_treatment=True,
    )

    result = pipeline.run(df)
    assert isinstance(result, PipelineResult)
    assert result.metadata.treatment_action == "median"
    assert result.processed_df["val"].iloc[3] != 100.0  # Median replaced 100.0


def test_pipeline_validation_failure_empty_df():
    pipeline = ProcessingPipeline(column_name="val", detection_method="zscore")
    empty_df = pd.DataFrame()

    with pytest.raises(OutlierEngineError):
        pipeline.run(empty_df)


def test_pipeline_validation_failure_missing_column():
    pipeline = ProcessingPipeline(
        column_name="missing_col", detection_method="zscore")
    df = pd.DataFrame({"val": [1.0, 2.0, 3.0]})

    with pytest.raises(OutlierEngineError):
        pipeline.run(df)


def test_pipeline_detection_failure_invalid_method():
    pipeline = ProcessingPipeline(
        column_name="val", detection_method="non_existent_method")
    df = pd.DataFrame({"val": [1.0, 2.0, 3.0]})

    with pytest.raises(OutlierEngineError):
        pipeline.run(df)


def test_pipeline_treatment_failure_invalid_action():
    pipeline = ProcessingPipeline(
        column_name="val",
        detection_method="zscore",
        treatment_action="non_existent_action",
    )
    df = pd.DataFrame({"val": [10.0, 12.0, 11.0, 100.0, 10.5]})

    with pytest.raises(OutlierEngineError):
        pipeline.run(df)
