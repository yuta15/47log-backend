"""Use case for deactivating the current user."""

from ...domain import UserIdVo, UserStatus
from ..exceptions import UserNotFoundError
from ..repositories.user_repository import UserRepository


class DeactivateUserUsecase:
    """Disable an existing user, leaving disabled users unchanged."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def execute(self, user_id: UserIdVo) -> None:
        """Disable and persist an enabled user.

        Raises:
            UserNotFoundError: If the user does not exist.
        """
        user = self._user_repository.get_user(user_id)
        if user is None:
            raise UserNotFoundError
        if user.status is UserStatus.DISABLED:
            return

        user.disable()
        self._user_repository.update_user(user)
