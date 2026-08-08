"""Base plugin abstract interface module."""

from abc import ABC, abstractmethod
from typing import Type
from outlier_engine.plugins.plugin_manifest import PluginManifest
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.treatments.base import BaseTreatment


class BasePlugin(ABC):
    """Abstract base class for all external Outlier Engine plugins."""

    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Return the plugin manifest."""
        pass

    @abstractmethod
    def register(self) -> None:
        """Hook method called during plugin loading to register components."""
        pass
