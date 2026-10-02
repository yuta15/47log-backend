"""Current-user use case test fixtures."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from src.modules.shared.domain import Clock
from src.modules.user_management.application import (
    GetCurrentUserUsecase,
    UserRepository,
)
from src.modules.user_management.domain import User, UserIdVo, UserStatus
from src.modules.user_management.domain.entities.value_objects import AccountNameVo


@pytest.fixture
def user_id() -> UserIdVo:
    """固定のユーザー ID を提供する。"""
    return UserIdVo("109876543210987654321")


@pytest.fixture
def user(user_id: UserIdVo) -> User:
    """作成日時と更新日時が異なる有効ユーザーを提供する。"""
    return User(
        user_id=user_id,
        account_name=AccountNameVo("dummy-account"),
        created_at=datetime(2026, 9, 29, 13, 39, 42, tzinfo=UTC),
        updated_at=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
        status=UserStatus.ENABLED,
        clock=Mock(spec=Clock),
    )


@pytest.fixture
def repository(user: User) -> Mock:
    """有効ユーザーを返す Repository の Mock を提供する。"""
    repository = Mock(spec=UserRepository)
    repository.get_user.return_value = user
    return repository


@pytest.fixture
def usecase(repository: Mock) -> GetCurrentUserUsecase:
    """Repository を注入した GetCurrentUserUsecase を提供する。"""
    return GetCurrentUserUsecase(repository)
