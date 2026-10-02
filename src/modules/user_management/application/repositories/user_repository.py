"""User repository contract."""

from abc import ABC, abstractmethod

from ...domain import User, UserIdVo


class UserRepository(ABC):
    """Define persistence operations for users."""

    @abstractmethod
    def get_user(self, user_id: UserIdVo) -> User | None:
        """Retrieve a user by ID, or return ``None`` when it does not exist."""

    @abstractmethod
    def create_user(self, user: User) -> None:
        """Create a user."""

    @abstractmethod
    def update_user(self, user: User) -> None:
        """Persist the user's account name, status, and modification timestamp.

        Raises:
            UserNotFoundError: If the user does not exist.
        """
