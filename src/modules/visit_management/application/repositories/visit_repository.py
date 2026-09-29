"""Visit repository contract."""

from abc import ABC, abstractmethod
from uuid import UUID

from ...domain import Visit


class VisitRepository(ABC):
    """Define persistence operations for visits."""

    @abstractmethod
    def list_visits(self, user_id: UUID) -> list[Visit]:
        """List visits for a user."""

    @abstractmethod
    def create_visit(self, visit: Visit) -> None:
        """Create a visit."""

    @abstractmethod
    def delete_visit(self, user_id: UUID, visit_id: UUID) -> None:
        """Delete a user's visit by ID."""
