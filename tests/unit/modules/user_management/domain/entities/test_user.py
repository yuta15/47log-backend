"""User domain rule tests."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from src.modules.user_management.domain import (
    User,
    UserDisabledError,
    UserIdVo,
    UserStatus,
)
from src.modules.user_management.domain.entities.value_objects import AccountNameVo


@pytest.mark.parametrize("status", [UserStatus.ENABLED, UserStatus.DISABLED])
def test_init_success_exposes_given_values(
    user_id: UserIdVo,
    account_name: AccountNameVo,
    created_at: datetime,
    updated_at: datetime,
    status: UserStatus,
    clock: Mock,
) -> None:
    """コンストラクタに渡した値を各プロパティから取得できることを確認する。"""
    # Act
    user = User(
        user_id=user_id,
        account_name=account_name,
        created_at=created_at,
        updated_at=updated_at,
        status=status,
        clock=clock,
    )

    # Assert
    assert user.user_id == user_id
    assert user.account_name == account_name
    assert user.created_at == created_at
    assert user.updated_at == updated_at
    assert user.status is status


def test_new_success_creates_enabled_user_with_clock_timestamps(
    user_id: UserIdVo, account_name: AccountNameVo, clock: Mock, updated_at: datetime
) -> None:
    """指定した ID と名前で有効ユーザーを作り、両日時に Clock の日時を設定する。"""
    # Act
    user = User.new(user_id, account_name, clock=clock)

    # Assert
    assert user.user_id == user_id
    assert user.account_name == account_name
    assert user.status is UserStatus.ENABLED
    assert user.created_at == updated_at
    assert user.updated_at == updated_at


@pytest.mark.parametrize("status", [UserStatus.ENABLED, UserStatus.DISABLED])
def test_enable_success_sets_enabled_status_and_updates_timestamp(
    user: User,
    user_id: UserIdVo,
    account_name: AccountNameVo,
    created_at: datetime,
    updated_at: datetime,
) -> None:
    """元の状態にかかわらず有効化して更新日時を変更し、他の属性を維持する。"""
    # Act
    user.enable()

    # Assert
    assert user.status is UserStatus.ENABLED
    assert user.updated_at == updated_at
    assert user.user_id == user_id
    assert user.account_name == account_name
    assert user.created_at == created_at


@pytest.mark.parametrize("status", [UserStatus.ENABLED, UserStatus.DISABLED])
def test_disable_success_sets_disabled_status_and_updates_timestamp(
    user: User,
    user_id: UserIdVo,
    account_name: AccountNameVo,
    created_at: datetime,
    updated_at: datetime,
) -> None:
    """元の状態にかかわらず無効化して更新日時を変更し、他の属性を維持する。"""
    # Act
    user.disable()

    # Assert
    assert user.status is UserStatus.DISABLED
    assert user.updated_at == updated_at
    assert user.user_id == user_id
    assert user.account_name == account_name
    assert user.created_at == created_at


@pytest.mark.parametrize("new_name", ["dummy-account", "renamed-account"])
def test_update_account_name_success_sets_name_and_updates_timestamp(
    user: User,
    user_id: UserIdVo,
    created_at: datetime,
    updated_at: datetime,
    new_name: str,
) -> None:
    """有効ユーザーの名前を設定し、同名でも更新日時を変更して他の属性を維持する。"""
    # Arrange
    account_name = AccountNameVo(new_name)

    # Act
    user.update_account_name(account_name)

    # Assert
    assert user.account_name == account_name
    assert user.updated_at == updated_at
    assert user.user_id == user_id
    assert user.created_at == created_at
    assert user.status is UserStatus.ENABLED


@pytest.mark.parametrize(
    ("status", "new_name"),
    [
        (UserStatus.DISABLED, "dummy-account"),
        (UserStatus.DISABLED, "renamed-account"),
    ],
)
def test_update_account_name_failure_rejects_disabled_user_without_changes(
    user: User,
    user_id: UserIdVo,
    account_name: AccountNameVo,
    created_at: datetime,
    new_name: str,
) -> None:
    """無効ユーザーは同名・別名への変更を拒否し、すべての属性を維持する。"""
    # Arrange
    new_account_name = AccountNameVo(new_name)

    # Assert
    with pytest.raises(UserDisabledError):
        user.update_account_name(new_account_name)

    assert user.account_name == account_name
    assert user.updated_at == created_at
    assert user.user_id == user_id
    assert user.created_at == created_at
    assert user.status is UserStatus.DISABLED
