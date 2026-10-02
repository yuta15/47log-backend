"""User repository contract."""

from abc import ABC, abstractmethod
from uuid import UUID

from ...domain import User


class UserRepository(ABC):
    """Define persistence operations for users."""

    @abstractmethod
    def get_user(self, user_id: UUID) -> User | None:
        """Retrieve a user by ID, or return ``None`` when it does not exist."""

    @abstractmethod
    def create_user(self, user: User) -> None:
        """Create a user."""

    @abstractmethod
    def disable_user(self, user_id: UUID) -> None:
        """Disable a user and update its ``updated_at`` timestamp.

        Raises:
            UserNotFoundError: If the user does not exist.
        """

    @abstractmethod
    def enable_user(self, user_id: UUID) -> None:
        """Enable a user and update its ``updated_at`` timestamp.

        Raises:
            UserNotFoundError: If the user does not exist.
        """
