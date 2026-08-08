"""Registry for managing and instantiating outlier treatments."""

from typing import Dict, Type
from outlier_engine.treatments.base import BaseTreatment
from outlier_engine.exceptions import OutlierEngineError


class TreatmentRegistry:
    """Registry class to hold and retrieve treatment strategy instances."""

    _treatments: Dict[str, Type[BaseTreatment]] = {}

    @classmethod
    def register(cls, name: str, treatment_cls: Type[BaseTreatment]) -> None:
        """Register a new treatment class."""
        cls._treatments[name.lower()] = treatment_cls

    @classmethod
    def get(cls, name: str) -> BaseTreatment:
        """Retrieve and instantiate a registered treatment by name."""
        treatment_cls = cls._treatments.get(name.lower())
        if not treatment_cls:
            raise OutlierEngineError(f"Treatment '{name}' is not registered.")
        return treatment_cls()
