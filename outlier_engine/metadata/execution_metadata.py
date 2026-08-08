"""Execution metadata module for Outlier Engine."""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass(frozen=True)
class ExecutionMetadata:
    """Class capturing runtime metadata for an outlier processing execution."""

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    detector: str = ""
    treatment: str = ""
    columns: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize metadata object to dictionary."""
        return asdict(self)
