import pytest
from dataclasses import FrozenInstanceError
from outlier_engine.metadata import ExecutionMetadata, FrameworkInfo


def test_execution_metadata_creation():
    meta = ExecutionMetadata(
        detector="iqr",
        treatment="clip",
        columns=["col1"],
        parameters={"multiplier": 1.5},
    )
    assert meta.detector == "iqr"
    assert meta.treatment == "clip"
    assert meta.columns == ["col1"]
    assert meta.parameters["multiplier"] == 1.5
    assert meta.execution_id is not None
    assert meta.timestamp is not None


def test_execution_metadata_immutability():
    meta = ExecutionMetadata()
    with pytest.raises(FrozenInstanceError):
        meta.detector = "zscore"  # type: ignore


def test_execution_metadata_serialization():
    meta = ExecutionMetadata(detector="iqr", treatment="clip")
    d = meta.to_dict()
    assert isinstance(d, dict)
    assert d["detector"] == "iqr"


def test_framework_info():
    info = FrameworkInfo.get_info()
    assert info.name == "OutlierEngine"
    assert info.version == "1.0.0"
    assert info.python_version is not None
    assert info.platform_info is not None

    with pytest.raises(FrozenInstanceError):
        info.version = "2.0.0"  # type: ignore
