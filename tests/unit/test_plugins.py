import pytest
import pandas as pd
from dataclasses import FrozenInstanceError

from outlier_engine.plugins import PluginManifest, BasePlugin, PluginLoader
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.treatments.base import BaseTreatment
from outlier_engine.types import DetectionResult
from outlier_engine.exceptions import OutlierEngineError
from outlier_engine.registries import DetectionRegistry, TreatmentRegistry


class CustomDummyDetector(BaseDetector):
    def detect(self, series: pd.Series, **kwargs) -> DetectionResult:
        mask = series > 50
        return DetectionResult(
            mask=mask,
            lower_bound=None,
            upper_bound=50.0,
            method="custom_dummy",
            outlier_count=int(mask.sum()),
        )


class CustomDummyTreatment(BaseTreatment):
    def apply(self, series: pd.Series, detection_result: DetectionResult, **kwargs) -> pd.Series:
        s = series.copy()
        s[detection_result.mask] = 0
        return s


class ValidCustomPlugin(BasePlugin):
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="custom_plugin",
            version="1.0.0",
            description="A valid custom plugin",
            author="Dev",
            detectors=["custom_dummy"],
            treatments=["custom_zero"],
        )

    def register(self) -> None:
        PluginLoader.register_detector("custom_dummy", CustomDummyDetector)
        PluginLoader.register_treatment("custom_zero", CustomDummyTreatment)


class InvalidManifestPlugin(BasePlugin):
    @property
    def manifest(self) -> PluginManifest:
        return None  # type: ignore

    def register(self) -> None:
        pass


class EmptyNamePlugin(BasePlugin):
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(name="", version="1.0.0", description="No name")

    def register(self) -> None:
        pass


def test_valid_manifest_creation():
    manifest = PluginManifest("p1", "1.0", "desc", "author", ["d1"], ["t1"])
    assert manifest.name == "p1"
    assert manifest.version == "1.0"
    with pytest.raises(FrozenInstanceError):
        manifest.name = "p2"  # type: ignore


def test_plugin_loader_success():
    loader = PluginLoader()
    plugin = ValidCustomPlugin()
    loader.load_plugin(plugin)

    assert "custom_plugin" in loader.loaded_plugins
    assert isinstance(DetectionRegistry.get("custom_dummy"), CustomDummyDetector)
    assert isinstance(TreatmentRegistry.get("custom_zero"), CustomDummyTreatment)


def test_plugin_loader_duplicate_prevention():
    loader = PluginLoader()
    plugin = ValidCustomPlugin()
    loader.load_plugin(plugin)

    with pytest.raises(OutlierEngineError, match="Plugin duplicate registration"):
        loader.load_plugin(plugin)


def test_plugin_loader_invalid_plugin_object():
    loader = PluginLoader()
    with pytest.raises(OutlierEngineError, match="Invalid plugin object"):
        loader.load_plugin("not_a_plugin")  # type: ignore


def test_plugin_loader_invalid_manifest():
    loader = PluginLoader()
    with pytest.raises(OutlierEngineError, match="Invalid plugin manifest"):
        loader.load_plugin(InvalidManifestPlugin())


def test_plugin_loader_empty_name():
    loader = PluginLoader()
    with pytest.raises(OutlierEngineError, match="Name cannot be empty"):
        loader.load_plugin(EmptyNamePlugin())
