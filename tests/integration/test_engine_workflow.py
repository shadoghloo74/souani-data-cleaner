import pytest
import pandas as pd
import numpy as np

from outlier_engine.engine import OutlierEngine
from outlier_engine.registries import DetectionRegistry, TreatmentRegistry
from outlier_engine.services import DetectionService, TreatmentService
from outlier_engine.detectors import (
    IQRDetector, ZScoreDetector, ModifiedZScoreDetector, PercentileDetector, StdDevDetector
)
from outlier_engine.treatments import (
    ClipTreatment, MeanTreatment, MedianTreatment, ConstantTreatment, DropRowsTreatment, FlagTreatment
)
from outlier_engine.types import DetectionResult
from outlier_engine.exceptions import OutlierEngineError


@pytest.fixture
def sample_series():
    """Series containing 9 normal values and 2 extreme outliers."""
    data = [10.0, 12.0, 11.0, 13.0, 12.0, 10.0, 11.0, 12.0, 13.0, 100.0, -50.0]
    return pd.Series(data, name="test_col")


@pytest.fixture
def sample_dataframe():
    """DataFrame for end-to-end testing."""
    return pd.DataFrame({
        "feature1": [10.0, 12.0, 11.0, 13.0, 12.0, 10.0, 11.0, 12.0, 13.0, 100.0, -50.0],
        "feature2": [5.0, 6.0, 5.5, 6.2, 5.8, 5.1, 5.9, 6.0, 5.7, 5.5, 6.1]
    })


# ==========================================
# A) Registry Tests
# ==========================================

def test_registry_default_detectors():
    expected_detectors = ["iqr", "zscore", "modified_zscore", "percentile", "std_dev"]
    for name in expected_detectors:
        detector = DetectionRegistry.get(name)
        assert detector is not None


def test_registry_default_treatments():
    expected_treatments = ["clip", "mean", "median", "constant", "drop_rows", "flag"]
    for name in expected_treatments:
        treatment = TreatmentRegistry.get(name)
        assert treatment is not None


def test_registry_unregistered_strategy_raises_error():
    with pytest.raises(OutlierEngineError):
        DetectionRegistry.get("invalid_detector")

    with pytest.raises(OutlierEngineError):
        TreatmentRegistry.get("invalid_treatment")


# ==========================================
# B) Detection Tests
# ==========================================

def test_iqr_detector(sample_series):
    detector = IQRDetector()
    res = detector.detect(sample_series, multiplier=1.5)
    assert isinstance(res, DetectionResult)
    assert res.outlier_count == 2
    assert res.mask.iloc[9] is True or res.mask.iloc[9] == 1
    assert res.mask.iloc[10] is True or res.mask.iloc[10] == 1


def test_zscore_detector(sample_series):
    detector = ZScoreDetector()
    res = detector.detect(sample_series, threshold=2.0)
    assert isinstance(res, DetectionResult)
    assert res.outlier_count >= 1


def test_modified_zscore_detector(sample_series):
    detector = ModifiedZScoreDetector()
    res = detector.detect(sample_series, threshold=3.5)
    assert isinstance(res, DetectionResult)
    assert res.outlier_count >= 1


def test_percentile_detector(sample_series):
    detector = PercentileDetector()
    res = detector.detect(sample_series, lower_quantile=0.05, upper_quantile=0.95)
    assert isinstance(res, DetectionResult)
    assert res.outlier_count >= 1


def test_std_dev_detector(sample_series):
    detector = StdDevDetector()
    res = detector.detect(sample_series, n_std=2.0)
    assert isinstance(res, DetectionResult)
    assert res.outlier_count >= 1


# ==========================================
# C) Treatment Tests
# ==========================================

def test_clip_treatment(sample_series):
    det_res = IQRDetector().detect(sample_series, multiplier=1.5)
    treated = ClipTreatment().apply(sample_series, det_res)
    assert treated.iloc[9] == det_res.upper_bound
    assert treated.iloc[10] == det_res.lower_bound


def test_mean_treatment(sample_series):
    det_res = IQRDetector().detect(sample_series, multiplier=1.5)
    treated = MeanTreatment().apply(sample_series, det_res)
    clean_mean = sample_series[~det_res.mask].mean()
    assert np.isclose(treated.iloc[9], clean_mean)


def test_median_treatment(sample_series):
    det_res = IQRDetector().detect(sample_series, multiplier=1.5)
    treated = MedianTreatment().apply(sample_series, det_res)
    clean_median = sample_series[~det_res.mask].median()
    assert np.isclose(treated.iloc[9], clean_median)


def test_constant_treatment(sample_series):
    det_res = IQRDetector().detect(sample_series, multiplier=1.5)
    treated = ConstantTreatment().apply(sample_series, det_res, fill_value=0.0)
    assert treated.iloc[9] == 0.0
    assert treated.iloc[10] == 0.0


def test_drop_rows_treatment(sample_series):
    det_res = IQRDetector().detect(sample_series, multiplier=1.5)
    treated = DropRowsTreatment().apply(sample_series, det_res)
    assert pd.isna(treated.iloc[9])
    assert pd.isna(treated.iloc[10])


def test_flag_treatment(sample_series):
    det_res = IQRDetector().detect(sample_series, multiplier=1.5)
    treated = FlagTreatment().apply(sample_series, det_res)
    assert treated.equals(sample_series)


# ==========================================
# D) Service Tests
# ==========================================

def test_services_delegation(sample_series):
    det_res = DetectionService.detect_column(sample_series, "test_col", method="iqr", multiplier=1.5)
    assert isinstance(det_res, DetectionResult)
    assert det_res.outlier_count == 2

    treated = TreatmentService.treat_column(sample_series, det_res, action="clip")
    assert treated.iloc[9] == det_res.upper_bound


# ==========================================
# E) Engine Workflow Test (End-to-End)
# ==========================================

def test_engine_full_workflow(sample_dataframe):
    engine = OutlierEngine()
    summary = engine.process(
        df=sample_dataframe,
        columns=["feature1"],
        method="iqr",
        action="clip"
    )

    assert summary.total_outliers_detected == 2
    assert len(summary.processed_df) == len(sample_dataframe)
    assert "feature1" in summary.column_results
    assert summary.column_results["feature1"].detection_result.outlier_count == 2
    assert summary.processed_df["feature2"].equals(sample_dataframe["feature2"])
