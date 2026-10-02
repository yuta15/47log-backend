"""User domain entity test fixtures."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from src.modules.shared.domain import Clock
from src.modules.user_management.domain import User, UserIdVo, UserStatus
from src.modules.user_management.domain.entities.value_objects import AccountNameVo


@pytest.fixture
def user_id() -> UserIdVo:
    """固定のユーザー ID を提供する。"""
    return UserIdVo("109876543210987654321")


@pytest.fixture
def account_name() -> AccountNameVo:
    """有効なアカウント名を提供する。"""
    return AccountNameVo("dummy-account")


@pytest.fixture
def created_at() -> datetime:
    """固定の作成日時を提供する。"""
    return datetime(2026, 9, 29, 13, 39, 42, tzinfo=UTC)


@pytest.fixture
def updated_at() -> datetime:
    """作成日時と異なる固定の更新日時を提供する。"""
    return datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


@pytest.fixture
def clock(updated_at: datetime) -> Mock:
    """更新日時を返す Clock の Mock を提供する。"""
    clock = Mock(spec=Clock)
    clock.now.return_value = updated_at
    return clock


@pytest.fixture
def status() -> UserStatus:
    """既定のユーザー状態を提供する。"""
    return UserStatus.ENABLED


@pytest.fixture
def user(
    user_id: UserIdVo,
    account_name: AccountNameVo,
    created_at: datetime,
    status: UserStatus,
    clock: Mock,
) -> User:
    """指定された状態のユーザーを提供する。"""
    return User(
        user_id=user_id,
        account_name=account_name,
        created_at=created_at,
        updated_at=created_at,
        status=status,
        clock=clock,
    )
