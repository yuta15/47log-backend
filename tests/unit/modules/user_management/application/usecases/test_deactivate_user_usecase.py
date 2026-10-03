"""DeactivateUserUsecase tests."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from src.modules.shared.domain import Clock
from src.modules.user_management.application import (
    DeactivateUserUsecase,
    UserNotFoundError,
    UserRepositoryError,
)
from src.modules.user_management.domain import User, UserIdVo, UserStatus


@pytest.fixture
def now() -> datetime:
    """無効化時の UTC 時刻を固定する。"""
    return datetime(2026, 10, 4, 0, 0, tzinfo=UTC)


@pytest.fixture
def enabled_user(user: User, now: datetime) -> User:
    """既存のユーザー属性と固定 Clock を持つ有効ユーザーを提供する。"""
    clock = Mock(spec=Clock)
    clock.now.return_value = now
    return User(
        user_id=user.user_id,
        account_name=user.account_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        status=UserStatus.ENABLED,
        clock=clock,
    )


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
def deactivate_usecase(repository: Mock) -> DeactivateUserUsecase:
    """Repository を注入した無効化 Usecase を提供する。"""
    return DeactivateUserUsecase(repository)


def test_execute_success_disables_enabled_user(
    deactivate_usecase: DeactivateUserUsecase,
    repository: Mock,
    enabled_user: User,
    user: User,
    user_id: UserIdVo,
    now: datetime,
) -> None:
    """指定 ID の有効ユーザーを無効化して保存し、更新対象以外の属性を維持する。"""
    # Arrange
    repository.get_user.return_value = enabled_user

    # Act
    deactivate_usecase.execute(user_id)

    # Assert
    repository.get_user.assert_called_once_with(user_id)
    repository.update_user.assert_called_once_with(enabled_user)
    assert enabled_user.status is UserStatus.DISABLED
    assert enabled_user.updated_at == now
    assert enabled_user.user_id == user.user_id
    assert enabled_user.account_name == user.account_name
    assert enabled_user.created_at == user.created_at


def test_execute_success_keeps_disabled_user_unchanged(
    deactivate_usecase: DeactivateUserUsecase,
    repository: Mock,
    disabled_user: User,
    user_id: UserIdVo,
) -> None:
    """無効ユーザーの全属性を維持し、保存処理を呼ばない。"""
    # Arrange
    repository.get_user.return_value = disabled_user
    before = (
        disabled_user.user_id,
        disabled_user.account_name,
        disabled_user.created_at,
        disabled_user.updated_at,
        disabled_user.status,
    )

    # Act
    deactivate_usecase.execute(user_id)

    # Assert
    assert (
        disabled_user.user_id,
        disabled_user.account_name,
        disabled_user.created_at,
        disabled_user.updated_at,
        disabled_user.status,
    ) == before
    repository.update_user.assert_not_called()


def test_execute_failure_raises_when_user_does_not_exist(
    deactivate_usecase: DeactivateUserUsecase, repository: Mock, user_id: UserIdVo
) -> None:
    """未登録の場合は UserNotFoundError を送出し、保存処理を呼ばない。"""
    # Arrange
    repository.get_user.return_value = None

    # Assert
    with pytest.raises(UserNotFoundError):
        deactivate_usecase.execute(user_id)
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
    deactivate_usecase: DeactivateUserUsecase,
    repository: Mock,
    enabled_user: User,
    user_id: UserIdVo,
    operation: str,
    error: Exception,
) -> None:
    """取得・保存時の例外を伝播し、取得失敗時は保存処理を呼ばない。"""
    # Arrange
    repository.get_user.return_value = enabled_user
    getattr(repository, operation).side_effect = error

    # Assert
    with pytest.raises(type(error)) as raised:
        deactivate_usecase.execute(user_id)
    assert raised.value is error
    if operation == "get_user":
        repository.update_user.assert_not_called()
