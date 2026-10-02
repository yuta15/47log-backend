"""DynamoDBUserRepository の統合テスト。"""

from datetime import datetime
from uuid import UUID

import pytest

from src.modules.user_management.application import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.modules.user_management.domain import User, UserStatus

pytestmark = pytest.mark.integration


def test_create_user_success_persists_and_reads_user(repository, user: User) -> None:
    """作成したユーザーを DynamoDB Local から取得できることを確認する。"""
    # Act
    repository.create_user(user)
    actual_user = repository.get_user(user.user_id)

    # Assert
    assert actual_user == user


def test_create_user_failure_raises_when_user_already_exists(
    repository, user: User
) -> None:
    """同一ユーザーを重複作成できないことを確認する。"""
    # Arrange
    repository.create_user(user)

    # Assert
    with pytest.raises(UserAlreadyExistsError):
        repository.create_user(user)


def test_disable_user_success_updates_status_and_updated_at(
    repository, updated_at: datetime, user: User
) -> None:
    """無効化により status と更新日時が保存されることを確認する。"""
    # Arrange
    repository.create_user(user)

    # Act
    repository.disable_user(user.user_id)
    actual_user = repository.get_user(user.user_id)

    # Assert
    assert actual_user is not None
    assert actual_user.status is UserStatus.DISABLED
    assert actual_user.updated_at == updated_at
    assert actual_user.created_at == user.created_at


def test_enable_user_success_updates_status_and_updated_at(
    repository, updated_at: datetime, user: User
) -> None:
    """有効化により status と更新日時が保存されることを確認する。"""
    # Arrange
    repository.create_user(user)

    # Act
    repository.enable_user(user.user_id)
    actual_user = repository.get_user(user.user_id)

    # Assert
    assert actual_user is not None
    assert actual_user.status is UserStatus.ENABLED
    assert actual_user.updated_at == updated_at
    assert actual_user.created_at == user.created_at


@pytest.mark.parametrize("method_name", ["disable_user", "enable_user"])
def test_update_user_failure_raises_when_user_does_not_exist(
    repository, user_id: UUID, method_name: str
) -> None:
    """未登録ユーザーの状態変更で暗黙作成されないことを確認する。"""
    # Assert
    with pytest.raises(UserNotFoundError):
        getattr(repository, method_name)(user_id)
