"""Registry for managing and instantiating outlier detectors."""

from typing import Dict, Type
from outlier_engine.detectors.base import BaseDetector
from outlier_engine.exceptions import OutlierEngineError


class DetectionRegistry:
    """Registry class to hold and retrieve detector strategy instances."""

    _detectors: Dict[str, Type[BaseDetector]] = {}

    @classmethod
    def register(cls, name: str, detector_cls: Type[BaseDetector]) -> None:
        """Register a new detector class."""
        cls._detectors[name.lower()] = detector_cls

    @classmethod
    def get(cls, name: str) -> BaseDetector:
        """Retrieve and instantiate a registered detector by name."""
        detector_cls = cls._detectors.get(name.lower())
        if not detector_cls:
            raise OutlierEngineError(f"Detector '{name}' is not registered.")
        return detector_cls()
