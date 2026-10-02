"""GetCurrentUserUsecase tests."""

from unittest.mock import Mock

import pytest

from src.modules.user_management.application import (
    GetCurrentUserOutput,
    GetCurrentUserUsecase,
    UserForbiddenError,
    UserNotFoundError,
)
from src.modules.user_management.domain import User, UserIdVo


def test_execute_success_returns_enabled_user_details(
    usecase: GetCurrentUserUsecase, repository: Mock, user: User, user_id: UserIdVo
) -> None:
    """有効ユーザーを取得して名前・作成日時・更新日時・状態を返すことを確認する。"""
    # Act
    output = usecase.execute(user_id)

    # Assert
    assert output == GetCurrentUserOutput(
        account_name=user.account_name.value,
        created_at=user.created_at,
        updated_at=user.updated_at,
        status=user.status,
    )
    repository.get_user.assert_called_once_with(user_id)


def test_execute_failure_raises_when_user_does_not_exist(
    usecase: GetCurrentUserUsecase, repository: Mock, user_id: UserIdVo
) -> None:
    """未登録ユーザーの場合は UserNotFoundError を返すことを確認する。"""
    # Arrange
    repository.get_user.return_value = None

    # Assert
    with pytest.raises(UserNotFoundError):
        usecase.execute(user_id)


def test_execute_failure_raises_when_user_is_disabled(
    usecase: GetCurrentUserUsecase, user: User, user_id: UserIdVo
) -> None:
    """無効ユーザーの場合は UserForbiddenError を返すことを確認する。"""
    # Arrange
    user.disable()

    # Assert
    with pytest.raises(UserForbiddenError):
        usecase.execute(user_id)
