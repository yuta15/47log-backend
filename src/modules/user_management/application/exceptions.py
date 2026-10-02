"""Application exceptions for user management."""


class UserForbiddenError(Exception):
    """Raised when the user's status does not permit an operation."""


class UserRepositoryError(Exception):
    """Raised when user persistence fails unexpectedly."""


class UserNotFoundError(UserRepositoryError):
    """Raised when a requested user does not exist."""


class UserAlreadyExistsError(UserRepositoryError):
    """Raised when creating a user that already exists."""
