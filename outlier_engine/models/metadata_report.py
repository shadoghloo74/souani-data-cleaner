"""Metadata report data model."""

from dataclasses import dataclass, field, asdict
from typing import Dict, List


@dataclass(frozen=True)
class MetadataReport:
    """Data model capturing dataset metadata before/after processing."""

    total_rows: int
    total_columns: int
    processed_columns: List[str]
    numeric_columns: List[str]
    missing_values_count: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize data model to dictionary."""
        return asdict(self)
