"""ActivateUserUsecase tests."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from src.modules.shared.domain import Clock
from src.modules.user_management.application import (
    ActivateUserUsecase,
    UserNotFoundError,
    UserRepositoryError,
)
from src.modules.user_management.domain import User, UserIdVo, UserStatus


@pytest.fixture
def now() -> datetime:
    """有効化時の UTC 時刻を固定する。"""
    return datetime(2026, 10, 4, 0, 0, tzinfo=UTC)


@pytest.fixture
def disabled_user(user: User, now: datetime) -> User:
    """既存のユーザー属性と固定 Clock を持つ無効ユーザーを提供する。"""
    clock = Mock(spec=Clock)
    clock.now.return_value = now
    return User(
        user_id=user.user_id,
        account_name=user.account_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        status=UserStatus.DISABLED,
        clock=clock,
    )


@pytest.fixture
def activate_usecase(repository: Mock) -> ActivateUserUsecase:
    """Repository を注入した有効化 Usecase を提供する。"""
    return ActivateUserUsecase(repository)


def test_execute_success_enables_disabled_user(
    activate_usecase: ActivateUserUsecase,
    repository: Mock,
    disabled_user: User,
    user: User,
    user_id: UserIdVo,
    now: datetime,
) -> None:
    """指定 ID の無効ユーザーを有効化して保存し、更新対象以外の属性を維持する。"""
    # Arrange
    repository.get_user.return_value = disabled_user

    # Act
    activate_usecase.execute(user_id)

    # Assert
    repository.get_user.assert_called_once_with(user_id)
    repository.update_user.assert_called_once_with(disabled_user)
    assert disabled_user.status is UserStatus.ENABLED
    assert disabled_user.updated_at == now
    assert disabled_user.user_id == user.user_id
    assert disabled_user.account_name == user.account_name
    assert disabled_user.created_at == user.created_at


def test_execute_success_keeps_enabled_user_unchanged(
    activate_usecase: ActivateUserUsecase,
    repository: Mock,
    user: User,
    user_id: UserIdVo,
) -> None:
    """有効ユーザーの全属性を維持し、保存処理を呼ばない。"""
    # Arrange
    before = (
        user.user_id,
        user.account_name,
        user.created_at,
        user.updated_at,
        user.status,
    )

    # Act
    activate_usecase.execute(user_id)

    # Assert
    assert (
        user.user_id,
        user.account_name,
        user.created_at,
        user.updated_at,
        user.status,
    ) == before
    repository.update_user.assert_not_called()


def test_execute_failure_raises_when_user_does_not_exist(
    activate_usecase: ActivateUserUsecase, repository: Mock, user_id: UserIdVo
) -> None:
    """未登録の場合は UserNotFoundError を送出し、保存処理を呼ばない。"""
    # Arrange
    repository.get_user.return_value = None

    # Assert
    with pytest.raises(UserNotFoundError):
        activate_usecase.execute(user_id)
    repository.update_user.assert_not_called()


@pytest.mark.parametrize(
    ("operation", "error"),
    [
        ("get_user", UserRepositoryError("private details")),
        ("update_user", UserRepositoryError("private details")),
        ("update_user", UserNotFoundError("private details")),
    ],
)
def test_execute_failure_propagates_repository_error(
    activate_usecase: ActivateUserUsecase,
    repository: Mock,
    disabled_user: User,
    user_id: UserIdVo,
    operation: str,
    error: Exception,
) -> None:
    """取得・保存時の例外を伝播し、取得失敗時は保存処理を呼ばない。"""
    # Arrange
    repository.get_user.return_value = disabled_user
    getattr(repository, operation).side_effect = error

    # Assert
    with pytest.raises(type(error)) as raised:
        activate_usecase.execute(user_id)
    assert raised.value is error
    if operation == "get_user":
        repository.update_user.assert_not_called()
