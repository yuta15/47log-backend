"""DynamoDBUserRepository テスト用 fixture。"""

from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import UUID

import pytest

from src.modules.shared.infra import UtcClock
from src.modules.user_management.domain import User, UserStatus
from src.modules.user_management.infra.dynamodb_user_repository import (
    DynamoDBUserRepository,
)


@pytest.fixture
def user_id() -> UUID:
    """固定のユーザー ID を提供する。"""
    return UUID("ed9affb2-b079-4be9-9cdd-2f0c77f387ca")


@pytest.fixture
def created_at() -> datetime:
    """固定の作成日時を提供する。"""
    return datetime(2026, 9, 29, 13, 39, 42, tzinfo=UTC)


@pytest.fixture
def updated_at() -> datetime:
    """固定の更新日時を提供する。"""
    return datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


@pytest.fixture
def table() -> Mock:
    """users テーブルの Mock を提供する。"""
    table = Mock()

    class ConditionalCheckFailedException(Exception):
        """DynamoDB の条件付き書込み失敗を表す。"""

    table.meta.client.exceptions.ConditionalCheckFailedException = (
        ConditionalCheckFailedException
    )
    return table


@pytest.fixture
def conditional_check_failed_exception(table: Mock) -> type[Exception]:
    """条件付き書込み失敗を表す例外型を提供する。"""
    return table.meta.client.exceptions.ConditionalCheckFailedException


@pytest.fixture
def context(table: Mock) -> Mock:
    """users テーブルを返す DynamoDBContext の Mock を提供する。"""
    context = Mock()
    context.resource.Table.return_value = table
    return context


@pytest.fixture
def clock(updated_at: datetime) -> Mock:
    """固定日時を返す UtcClock の Mock を提供する。"""
    clock = Mock(spec=UtcClock)
    clock.now.return_value = updated_at
    return clock


@pytest.fixture
def repository(context: Mock, clock: Mock) -> DynamoDBUserRepository:
    """固定 UTC clock を持つ Repository を提供する。"""
    return DynamoDBUserRepository(
        context,
        table_name="users_table",
        clock=clock,
    )


@pytest.fixture
def user(user_id: UUID, created_at: datetime) -> User:
    """有効なユーザーを提供する。"""
    return User(
        user_id=user_id,
        account_name="dummy-account",
        created_at=created_at,
        updated_at=created_at,
        status=UserStatus.ENABLED,
    )
