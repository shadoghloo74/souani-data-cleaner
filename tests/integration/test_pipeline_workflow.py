import pandas as pd

from outlier_engine.pipelines import ProcessingPipeline, PipelineResult
from outlier_engine.plugins import PluginManifest, BasePlugin, PluginLoader
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.treatments.base import BaseTreatment
from outlier_engine.types import DetectionResult


# Standard Plugin for Integration Test
class PipeCustomDetector(BaseDetector):
    def detect(self, series: pd.Series, cutoff: float = 80.0, **kwargs) -> DetectionResult:
        mask = series > cutoff
        return DetectionResult(
            mask=mask,
            lower_bound=None,
            upper_bound=cutoff,
            method="pipe_custom_detector",
            outlier_count=int(mask.sum()),
        )


class PipeCustomTreatment(BaseTreatment):
    def apply(self, series: pd.Series, detection_result: DetectionResult, fill_value: float = -1.0, **kwargs) -> pd.Series:
        s = series.copy()
        s[detection_result.mask] = fill_value
        return s


class PipeTestPlugin(BasePlugin):
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="pipe_test_plugin",
            version="1.0.0",
            description="Plugin for pipeline integration test",
            author="Pipeline Team",
            detectors=["pipe_custom_detector"],
            treatments=["pipe_custom_treatment"],
        )

    def register(self) -> None:
        PluginLoader.register_detector(
            "pipe_custom_detector", PipeCustomDetector)
        PluginLoader.register_treatment(
            "pipe_custom_treatment", PipeCustomTreatment)


def test_pipeline_full_workflow_standard_components():
    # End-to-end flow with built-in detector & treatment
    df = pd.DataFrame({"salary": [3000.0, 3200.0, 3100.0, 50000.0, 3050.0]})

    pipeline = ProcessingPipeline(
        column_name="salary",
        detection_method="iqr",
        treatment_action="median",
        apply_treatment=True,
    )

    result = pipeline.run(df)

    assert isinstance(result, PipelineResult)
    assert result.detection_result.outlier_count == 1
    assert result.report is not None
    assert result.processed_df["salary"].iloc[3] < 50000.0


def test_pipeline_full_workflow_with_plugin_detector():
    # Load Plugin
    loader = PluginLoader()
    loader.load_plugin(PipeTestPlugin())

    # Data
    df = pd.DataFrame({"score": [10.0, 20.0, 30.0, 95.0, 100.0]})

    # Run Pipeline with Plugin components
    pipeline = ProcessingPipeline(
        column_name="score",
        detection_method="pipe_custom_detector",
        treatment_action="pipe_custom_treatment",
        apply_treatment=True,
        detection_kwargs={"cutoff": 80.0},
        treatment_kwargs={"fill_value": 0.0},
    )

    result = pipeline.run(df)

    assert isinstance(result, PipelineResult)
    assert result.detection_result.outlier_count == 2
    assert result.processed_df["score"].tolist() == [
        10.0, 20.0, 30.0, 0.0, 0.0]
    assert result.report is not None
    assert result.metadata.detection_method == "pipe_custom_detector"
    assert result.metadata.treatment_action == "pipe_custom_treatment"
