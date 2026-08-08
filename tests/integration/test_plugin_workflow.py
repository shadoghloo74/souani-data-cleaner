import pandas as pd

from outlier_engine.plugins import PluginManifest, BasePlugin, PluginLoader
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.treatments.base import BaseTreatment
from outlier_engine.types import DetectionResult
from outlier_engine.services import DetectionService, TreatmentService
from outlier_engine.registries import DetectionRegistry, TreatmentRegistry


class ThresholdDetectorPlugin(BaseDetector):
    def detect(self, series: pd.Series, threshold: float = 100.0, **kwargs) -> DetectionResult:
        mask = series > threshold
        return DetectionResult(
            mask=mask,
            lower_bound=None,
            upper_bound=threshold,
            method="custom_threshold",
            outlier_count=int(mask.sum()),
        )


class ZeroTreatmentPlugin(BaseTreatment):
    def apply(self, series: pd.Series, detection_result: DetectionResult, **kwargs) -> pd.Series:
        s = series.copy()
        s[detection_result.mask] = 0.0
        return s


class ExternalCustomExtensionPlugin(BasePlugin):
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="external_threshold_extension",
            version="1.0.0",
            description="External plugin adding threshold detector and zero treatment",
            author="Data Team",
            detectors=["custom_threshold"],
            treatments=["custom_zero_out"],
        )

    def register(self) -> None:
        PluginLoader.register_detector(
            "custom_threshold", ThresholdDetectorPlugin)
        PluginLoader.register_treatment("custom_zero_out", ZeroTreatmentPlugin)


def test_external_plugin_end_to_end_workflow():
    # 1. Load External Plugin via PluginLoader
    loader = PluginLoader()
    loader.load_plugin(ExternalCustomExtensionPlugin())

    # 2. Prepare Data
    df = pd.DataFrame({"val": [10.0, 50.0, 150.0, 200.0]})

    # 3. Test Detection Service with new plugin method
    det_res = DetectionService.detect_column(
        df["val"], "val", method="custom_threshold", threshold=100.0)
    assert det_res.outlier_count == 2

    # 4. Test Treatment Service with new plugin action
    treated_series = TreatmentService.treat_column(
        df["val"], det_res, action="custom_zero_out")
    assert treated_series.tolist() == [10.0, 50.0, 0.0, 0.0]

    # 5. Verify direct engine registry awareness
    det = DetectionRegistry.get("custom_threshold")
    res = det.detect(df["val"], threshold=100.0)
    trt = TreatmentRegistry.get("custom_zero_out")
    final_series = trt.apply(df["val"], res)
    assert final_series.tolist() == [10.0, 50.0, 0.0, 0.0]
