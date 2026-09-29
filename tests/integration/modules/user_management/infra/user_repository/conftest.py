"""DynamoDBUserRepository 統合テスト用 fixture。"""

import os
from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import UUID

import pytest

from src.modules.shared.infra import UtcClock
from src.modules.shared.infra.dynamodb import DynamoDBContext, DynamoDBSettings
from src.modules.user_management.domain import User, UserStatus
from src.modules.user_management.infra.dynamodb_user_repository import (
    DynamoDBUserRepository,
)


@pytest.fixture
def user_id(table) -> UUID:
    """テスト前後に削除する固定のユーザー ID を提供する。"""
    user_id = UUID("ed9affb2-b079-4be9-9cdd-2f0c77f387ca")
    key = {"user_id": str(user_id)}
    table.delete_item(Key=key)
    yield user_id
    table.delete_item(Key=key)


@pytest.fixture
def created_at() -> datetime:
    """固定の作成日時を提供する。"""
    return datetime(2026, 9, 29, 13, 39, 42, tzinfo=UTC)


@pytest.fixture
def updated_at() -> datetime:
    """固定の更新日時を提供する。"""
    return datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


@pytest.fixture
def context(monkeypatch) -> DynamoDBContext:
    """DynamoDB Local に接続する DynamoDBContext を提供する。"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "local")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "local")
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL", "http://localhost:8000")
    return DynamoDBContext(DynamoDBSettings(endpoint_url=endpoint_url))


@pytest.fixture
def table(context: DynamoDBContext, table_name: str):
    """DynamoDB Local の users テーブルを提供する。"""
    return context.resource.Table(table_name)


@pytest.fixture
def table_name() -> str:
    """users テーブル名を環境変数から提供する。"""
    return os.environ.get("USERS_TABLE_NAME", "users_table")


@pytest.fixture
def clock(updated_at: datetime) -> Mock:
    """固定日時を返す UtcClock の Mock を提供する。"""
    clock = Mock(spec=UtcClock)
    clock.now.return_value = updated_at
    return clock


@pytest.fixture
def repository(
    context: DynamoDBContext, table_name: str, clock: Mock
) -> DynamoDBUserRepository:
    """固定 UTC clock を持つ Repository を提供する。"""
    return DynamoDBUserRepository(
        context,
        table_name=table_name,
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
