"""Use case for retrieving the current enabled user."""

from dataclasses import dataclass
from datetime import datetime

from ...domain import UserIdVo, UserStatus
from ..exceptions import UserForbiddenError, UserNotFoundError
from ..repositories.user_repository import UserRepository


@dataclass(frozen=True)
class GetCurrentUserOutput:
    """Details returned for the current enabled user."""

    account_name: str
    created_at: datetime
    updated_at: datetime
    status: UserStatus


class GetCurrentUserUsecase:
    """Return current-user details only for an existing enabled user."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def execute(self, user_id: UserIdVo) -> GetCurrentUserOutput:
        """Return user details, rejecting missing or disabled users.

        Raises:
            UserNotFoundError: If the user does not exist.
            UserForbiddenError: If the user is not enabled.
        """
        user = self._user_repository.get_user(user_id)
        if user is None:
            raise UserNotFoundError
        if user.status is not UserStatus.ENABLED:
            raise UserForbiddenError

        return GetCurrentUserOutput(
            account_name=user.account_name.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
            status=user.status,
        )
