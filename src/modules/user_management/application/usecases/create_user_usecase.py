"""Use case for registering an authenticated user."""

from ....shared.domain import Clock
from ...domain import User, UserIdVo
from ...domain.entities.value_objects import AccountNameVo
from ..repositories.user_repository import UserRepository


class CreateUserUsecase:
    """Create an enabled user without overwriting an existing registration."""

    def __init__(self, user_repository: UserRepository, *, clock: Clock) -> None:
        """Use the supplied repository and clock to register users."""
        self._user_repository = user_repository
        self._clock = clock

    def execute(self, user_id: UserIdVo, account_name: AccountNameVo) -> None:
        """Persist a new user, propagating conflicts and persistence failures."""
        user = User.new(user_id, account_name, clock=self._clock)
        self._user_repository.create_user(user)
