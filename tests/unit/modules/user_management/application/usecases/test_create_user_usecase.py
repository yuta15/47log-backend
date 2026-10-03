"""CreateUserUsecase tests."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from src.modules.shared.domain import Clock
from src.modules.user_management.application import (
    CreateUserUsecase,
    UserAlreadyExistsError,
)
from src.modules.user_management.domain import UserIdVo, UserStatus
from src.modules.user_management.domain.entities.value_objects import AccountNameVo


@pytest.fixture
def created_at() -> datetime:
    """固定の UTC 作成日時を提供する。"""
    return datetime(2026, 10, 4, 0, 0, tzinfo=UTC)


@pytest.fixture
def clock(created_at: datetime) -> Mock:
    """固定日時を返す Clock の Mock を提供する。"""
    clock = Mock(spec=Clock)
    clock.now.return_value = created_at
    return clock


@pytest.fixture
def create_usecase(repository: Mock, clock: Mock) -> CreateUserUsecase:
    """Repository と固定 Clock を注入した登録 Usecase を提供する。"""
    repository.get_user.return_value = None
    return CreateUserUsecase(repository, clock=clock)


def test_execute_success_creates_enabled_user(
    create_usecase: CreateUserUsecase,
    repository: Mock,
    user_id: UserIdVo,
    created_at: datetime,
) -> None:
    """指定した ID と名前で有効ユーザーを作成し作成・更新日時を同じ UTC 時刻にする。"""
    # Arrange
    account_name = AccountNameVo("dummy-account")

    # Act
    create_usecase.execute(user_id, account_name)

    # Assert
    repository.create_user.assert_called_once()
    user = repository.create_user.call_args.args[0]
    assert user.user_id == user_id
    assert user.account_name == account_name
    assert user.status is UserStatus.ENABLED
    assert user.created_at == created_at
    assert user.updated_at == created_at


def test_execute_failure_propagates_duplicate_user_error(
    create_usecase: CreateUserUsecase,
    repository: Mock,
    user_id: UserIdVo,
) -> None:
    """保存時の同一 ID の競合を握りつぶさず呼び出し側に伝える。"""
    # Arrange
    repository.create_user.side_effect = UserAlreadyExistsError

    with pytest.raises(UserAlreadyExistsError):
        create_usecase.execute(user_id, AccountNameVo("dummy-account"))
