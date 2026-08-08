"""Execution context data model."""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict


@dataclass(frozen=True)
class ExecutionContext:
    """Data model storing execution configuration and metadata."""

    execution_id: str
    timestamp: str
    strict_numeric: bool = True
    inplace: bool = False
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize data model to dictionary."""
        return asdict(self)
