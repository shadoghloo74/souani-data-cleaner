"""Plugin manifest data model."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass(frozen=True)
class PluginManifest:
    """Data model describing plugin details, versioning, and capabilities."""

    name: str
    version: str
    description: str
    author: str = ""
    detectors: List[str] = field(default_factory=list)
    treatments: List[str] = field(default_factory=list)
    min_engine_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize plugin manifest to a dictionary."""
        return asdict(self)
