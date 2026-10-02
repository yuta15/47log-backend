"""Clock interface for domain operations."""

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Provide the current time in UTC."""

    def now(self) -> datetime:
        """Return the current UTC time as a timezone-aware datetime."""
        ...
