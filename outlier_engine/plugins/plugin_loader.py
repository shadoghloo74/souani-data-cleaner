"""Plugin loader module for loading and validating plugins."""

from typing import Dict, Type
from outlier_engine.plugins.base_plugin import BasePlugin
from outlier_engine.plugins.plugin_manifest import PluginManifest
from outlier_engine.exceptions import OutlierEngineError
from outlier_engine.registries import DetectionRegistry, TreatmentRegistry
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.treatments.base import BaseTreatment


class PluginLoader:
    """Loader responsible for validating plugins and registering their components."""

    def __init__(self) -> None:
        self._loaded_plugins: Dict[str, BasePlugin] = {}

    @property
    def loaded_plugins(self) -> Dict[str, BasePlugin]:
        """Return a dictionary of currently loaded plugins."""
        return self._loaded_plugins.copy()

    def validate_plugin(self, plugin: BasePlugin) -> None:
        """Validate a plugin instance and its manifest."""
        if not isinstance(plugin, BasePlugin):
            raise OutlierEngineError(
                "Invalid plugin object: Must inherit from BasePlugin.")

        manifest = plugin.manifest
        if not isinstance(manifest, PluginManifest):
            raise OutlierEngineError(
                "Invalid plugin manifest: Must be an instance of PluginManifest.")

        if not manifest.name or not isinstance(manifest.name, str) or not manifest.name.strip():
            raise OutlierEngineError(
                "Plugin validation failed: Name cannot be empty.")

        if not manifest.version or not isinstance(manifest.version, str) or not manifest.version.strip():
            raise OutlierEngineError(
                "Plugin validation failed: Version cannot be empty.")

        if manifest.name in self._loaded_plugins:
            raise OutlierEngineError(
                f"Plugin duplicate registration: Plugin '{manifest.name}' is already loaded.")

    def load_plugin(self, plugin: BasePlugin) -> None:
        """Validate, load, and register components from a plugin."""
        self.validate_plugin(plugin)
        plugin.register()
        self._loaded_plugins[plugin.manifest.name] = plugin

    @staticmethod
    def register_detector(method_name: str, detector_cls: Type[BaseDetector]) -> None:
        """Helper method to register custom detectors into DetectionRegistry."""
        if not issubclass(detector_cls, BaseDetector):
            raise OutlierEngineError(
                f"Class '{detector_cls.__name__}' must inherit from BaseDetector.")
        DetectionRegistry.register(method_name, detector_cls)

    @staticmethod
    def register_treatment(action_name: str, treatment_cls: Type[BaseTreatment]) -> None:
        """Helper method to register custom treatments into TreatmentRegistry."""
        if not issubclass(treatment_cls, BaseTreatment):
            raise OutlierEngineError(
                f"Class '{treatment_cls.__name__}' must inherit from BaseTreatment.")
        TreatmentRegistry.register(action_name, treatment_cls)
