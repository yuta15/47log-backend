"""Application exceptions for user management."""


class UserRepositoryError(Exception):
    """Raised when user persistence fails unexpectedly."""


class UserNotFoundError(UserRepositoryError):
    """Raised when a requested user does not exist."""


class UserAlreadyExistsError(UserRepositoryError):
    """Raised when creating a user that already exists."""
