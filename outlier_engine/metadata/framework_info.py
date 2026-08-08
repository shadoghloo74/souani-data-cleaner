"""Framework metadata and system information."""

import platform
import sys
from dataclasses import dataclass, field, asdict
from typing import Dict, Any


@dataclass(frozen=True)
class FrameworkInfo:
    """Class containing details about the framework and runtime environment."""

    name: str = "OutlierEngine"
    version: str = "1.0.0"
    python_version: str = field(default_factory=lambda: sys.version.split()[0])
    platform_info: str = field(default_factory=lambda: platform.system())

    @classmethod
    def get_info(cls) -> "FrameworkInfo":
        """Factory method returning framework info instance."""
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize framework info to dictionary."""
        return asdict(self)
