"""Base plugin abstract interface module."""

from abc import ABC, abstractmethod
from outlier_engine.plugins.plugin_manifest import PluginManifest


class BasePlugin(ABC):
    """Abstract base class for all external Outlier Engine plugins."""

    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Return the plugin manifest."""

    @abstractmethod
    def register(self) -> None:
        """Hook method called during plugin loading to register components."""
