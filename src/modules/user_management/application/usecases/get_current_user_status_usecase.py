"""Use case for retrieving the current user's registration status."""

from dataclasses import dataclass
from enum import Enum

from ...domain import UserIdVo
from ..repositories.user_repository import UserRepository


class CurrentUserStatus(Enum):
    """Represent persisted user states and the absence of a registered user."""

    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    UNREGISTERED = "UNREGISTERED"


@dataclass(frozen=True)
class GetCurrentUserStatusOutput:
    """Status returned for the authenticated user."""

    status: CurrentUserStatus


class GetCurrentUserStatusUsecase:
    """Return the registration status without creating or changing a user."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Use the supplied repository to look up the authenticated user."""
        self._user_repository = user_repository

    def execute(self, user_id: UserIdVo) -> GetCurrentUserStatusOutput:
        """Return the stored status, or UNREGISTERED when the user is absent."""
        user = self._user_repository.get_user(user_id)
        if user is None:
            status = CurrentUserStatus.UNREGISTERED
        else:
            status = CurrentUserStatus(user.status.value)
        return GetCurrentUserStatusOutput(status=status)
