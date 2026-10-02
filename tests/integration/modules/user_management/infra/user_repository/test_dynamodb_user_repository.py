"""DynamoDBUserRepository の統合テスト。"""

from datetime import datetime

import pytest

from src.modules.user_management.application import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.modules.user_management.domain import User, UserStatus
from src.modules.user_management.domain.entities.value_objects import AccountNameVo

pytestmark = pytest.mark.integration


def test_create_user_success_persists_and_reads_user(repository, user: User) -> None:
    """作成したユーザーを DynamoDB Local から取得できることを確認する。"""
    # Act
    repository.create_user(user)
    actual_user = repository.get_user(user.user_id)

    # Assert
    assert actual_user is not None
    assert actual_user.user_id == user.user_id
    assert actual_user.account_name == user.account_name
    assert actual_user.created_at == user.created_at
    assert actual_user.updated_at == user.updated_at
    assert actual_user.status is user.status


def test_create_user_failure_raises_when_user_already_exists(
    repository, user: User
) -> None:
    """同一ユーザーを重複作成できないことを確認する。"""
    # Arrange
    repository.create_user(user)

    # Assert
    with pytest.raises(UserAlreadyExistsError):
        repository.create_user(user)


@pytest.mark.parametrize(
    ("method_name", "expected_status"),
    [("enable", UserStatus.ENABLED), ("disable", UserStatus.DISABLED)],
)
def test_update_user_success_persists_status_and_updated_at(
    repository,
    updated_at: datetime,
    user: User,
    method_name: str,
    expected_status: UserStatus,
) -> None:
    """ドメインで変更した状態と更新日時が保存され、他の属性を維持する。"""
    # Arrange
    if method_name == "enable":
        user.disable()
    repository.create_user(user)

    # Act
    getattr(user, method_name)()
    repository.update_user(user)
    actual_user = repository.get_user(user.user_id)

    # Assert
    assert actual_user is not None
    assert actual_user.status is expected_status
    assert actual_user.updated_at == updated_at
    assert actual_user.created_at == user.created_at
    assert actual_user.account_name == user.account_name
    assert actual_user.user_id == user.user_id


def test_update_user_success_persists_account_name_and_updated_at(
    repository,
    updated_at: datetime,
    user: User,
) -> None:
    """ドメインで変更した名前と更新日時が保存され、他の属性を維持する。"""
    # Arrange
    repository.create_user(user)
    account_name = AccountNameVo("renamed-account")

    # Act
    user.update_account_name(account_name)
    repository.update_user(user)
    actual_user = repository.get_user(user.user_id)

    # Assert
    assert actual_user is not None
    assert actual_user.account_name == account_name
    assert actual_user.updated_at == updated_at
    assert actual_user.created_at == user.created_at
    assert actual_user.status is user.status
    assert actual_user.user_id == user.user_id


def test_update_user_failure_raises_when_user_does_not_exist(
    repository,
    user: User,
) -> None:
    """未登録ユーザーの更新を拒否し、暗黙作成されないことを確認する。"""
    # Assert
    with pytest.raises(UserNotFoundError):
        repository.update_user(user)

    assert repository.get_user(user.user_id) is None
