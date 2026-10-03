"""Current-user status use case tests."""

from unittest.mock import Mock

import pytest

from src.modules.user_management.application import (
    GetCurrentUserStatusUsecase,
)
from src.modules.user_management.domain import User, UserIdVo


@pytest.mark.parametrize(
    ("stored_status", "expected_status"),
    [("ENABLED", "ENABLED"), ("DISABLED", "DISABLED"), (None, "UNREGISTERED")],
)
def test_execute_success_returns_current_user_status(
    repository: Mock,
    user: User,
    user_id: UserIdVo,
    stored_status: str | None,
    expected_status: str,
) -> None:
    """本人の登録状態に応じて有効・無効・未登録の状態を返す。"""
    # Arrange
    if stored_status is None:
        repository.get_user.return_value = None
    elif stored_status == "DISABLED":
        user.disable()
    usecase = GetCurrentUserStatusUsecase(repository)

    # Act
    output = usecase.execute(user_id)

    # Assert
    assert output.status.value == expected_status
    repository.get_user.assert_called_once_with(user_id)
