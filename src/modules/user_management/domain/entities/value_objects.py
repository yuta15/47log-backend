"""User domain value objects."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class UserIdVo:
    """Immutable user identifier independent of identity providers."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise ValueError("User ID must be a string.")

        value = self.value.strip()
        if not value:
            raise ValueError("User ID must not be empty.")
        if len(value) > 255:
            raise ValueError("User ID must be at most 255 characters.")

        object.__setattr__(self, "value", value)


@dataclass(frozen=True)
class AccountNameVo:
    """Account name with at most 64 characters."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise ValueError("Account name must be a string.")

        match = re.fullmatch(
            r"[A-Za-z0-9](?:[A-Za-z0-9_-]{0,62}[A-Za-z0-9])?", self.value
        )
        if match is None:
            raise ValueError(
                "Account name must be 1-64 characters, start and end with an "
                "ASCII letter or digit, and contain only ASCII letters, digits, "
                "hyphens, or underscores."
            )
