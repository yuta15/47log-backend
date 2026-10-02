"""Domain exceptions for user management."""


class UserDisabledError(Exception):
    """Raised when a disabled user attempts a restricted operation."""
