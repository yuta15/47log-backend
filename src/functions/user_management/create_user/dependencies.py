"""Dependencies for the user registration endpoint."""

import os
from functools import cache

from ....modules.shared.infra.dynamodb import DynamoDBContext, DynamoDBSettings
from ....modules.shared.infra.utc_clock import UtcClock
from ....modules.user_management.application import CreateUserUsecase
from ....modules.user_management.infra.dynamodb_user_repository import (
    DynamoDBUserRepository,
)


@cache
def _get_usecase() -> CreateUserUsecase:
    """Reuse dependencies across invocations in one execution environment."""
    clock = UtcClock()
    repository = DynamoDBUserRepository(
        DynamoDBContext(DynamoDBSettings()),
        table_name=os.environ.get("USERS_TABLE_NAME", "users_table"),
        clock=clock,
    )
    return CreateUserUsecase(repository, clock=clock)
