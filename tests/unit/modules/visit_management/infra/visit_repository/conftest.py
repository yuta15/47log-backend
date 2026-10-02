"""DynamoDBVisitRepository の単体テスト用 fixture。"""

from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import UUID

import pytest

from src.modules.visit_management.domain import Prefecture, Visit
from src.modules.visit_management.infra.dynamodb_visit_repository import (
    DynamoDBVisitRepository,
)


@pytest.fixture
def user_id() -> UUID:
    """固定のユーザー ID を提供する。"""
    return UUID("f0a6ba9f-fdc5-453d-b7bd-2a1f12c3f3fb")


@pytest.fixture
def created_at() -> datetime:
    """固定の作成日時を提供する。"""
    return datetime(2026, 9, 29, 13, 39, 42, tzinfo=UTC)


@pytest.fixture
def visit(user_id: UUID, created_at: datetime) -> Visit:
    """固定の訪問記録を提供する。"""
    return Visit(
        user_id=user_id,
        visit_id=UUID("019994f0-0000-7000-8000-000000000001"),
        prefecture=Prefecture.HOKKAIDO,
        created_at=created_at,
    )


@pytest.fixture
def table() -> Mock:
    """visit テーブルと条件付き書込み失敗の例外型を提供する。"""
    table = Mock()

    class ConditionalCheckFailedException(Exception):
        """DynamoDB の条件付き書込み失敗を表す。"""

    table.meta.client.exceptions.ConditionalCheckFailedException = (
        ConditionalCheckFailedException
    )
    return table


@pytest.fixture
def conditional_check_failed_exception(table: Mock) -> type[Exception]:
    """条件付き書込み失敗の例外型を提供する。"""
    return table.meta.client.exceptions.ConditionalCheckFailedException


@pytest.fixture
def context(table: Mock) -> Mock:
    """visit テーブルを返す DynamoDBContext の Mock を提供する。"""
    context = Mock()
    context.resource.Table.return_value = table
    return context


@pytest.fixture
def repository(context: Mock) -> DynamoDBVisitRepository:
    """テーブルを差し替えた Repository を提供する。"""
    return DynamoDBVisitRepository(context, table_name="visit_table")
