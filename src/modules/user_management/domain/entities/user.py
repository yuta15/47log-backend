"""User domain entity."""

from datetime import datetime
from typing import Self

from ....shared.domain import Clock
from ..exceptions import UserDisabledError
from .enums import UserStatus
from .value_objects import AccountNameVo, UserIdVo


class User:
    """
    Represent a user.
    """

    def __init__(
        self,
        user_id: UserIdVo,
        account_name: AccountNameVo,
        created_at: datetime,
        updated_at: datetime,
        status: UserStatus,
        *,
        clock: Clock,
    ) -> None:
        self._user_id = user_id
        self._account_name = account_name
        self._created_at = created_at
        self._updated_at = updated_at
        self._status = status
        self._clock = clock

    @classmethod
    def new(
        cls, user_id: UserIdVo, account_name: AccountNameVo, *, clock: Clock
    ) -> Self:
        """Create an enabled user with UTC timestamps."""
        now = clock.now()
        return cls(
            user_id=user_id,
            account_name=account_name,
            created_at=now,
            updated_at=now,
            status=UserStatus.ENABLED,
            clock=clock,
        )

    def _update_updated_at(self) -> None:
        """Update the modification timestamp to the current UTC time."""
        self._updated_at = self._clock.now()

    def enable(self) -> None:
        """Enable the user and update the modification timestamp."""
        self._update_updated_at()
        self._status = UserStatus.ENABLED

    def disable(self) -> None:
        """Disable the user and update the modification timestamp."""
        self._update_updated_at()
        self._status = UserStatus.DISABLED

    def update_account_name(self, account_name: AccountNameVo) -> None:
        """Update the account name and modification timestamp."""
        if self._status is UserStatus.DISABLED:
            raise UserDisabledError("Disabled users cannot change their account name.")

        self._update_updated_at()
        self._account_name = account_name

    @property
    def user_id(self) -> UserIdVo:
        return self._user_id

    @property
    def account_name(self) -> AccountNameVo:
        return self._account_name

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def status(self) -> UserStatus:
        return self._status
