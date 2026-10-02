"""DynamoDBVisitRepository の統合テスト用 fixture。"""

import os
from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from src.modules.shared.infra.dynamodb import DynamoDBContext, DynamoDBSettings
from src.modules.visit_management.domain import Prefecture, Visit
from src.modules.visit_management.infra.dynamodb_visit_repository import (
    DynamoDBVisitRepository,
)


@pytest.fixture
def context(monkeypatch) -> DynamoDBContext:
    """ローカル用の認証情報で DynamoDB Local に接続する。"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "local")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "local")
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL", "http://localhost:8000")
    return DynamoDBContext(DynamoDBSettings(endpoint_url=endpoint_url))


@pytest.fixture
def table_name() -> str:
    """訪問記録のテーブル名を提供する。"""
    return os.environ.get("VISIT_TABLE_NAME", "visit_table")


@pytest.fixture
def table(context: DynamoDBContext, table_name: str):
    """DynamoDB Local の訪問記録テーブルを提供する。"""
    return context.resource.Table(table_name)


@pytest.fixture
def repository(context: DynamoDBContext, table_name: str) -> DynamoDBVisitRepository:
    """DynamoDB Local を利用する Repository を提供する。"""
    return DynamoDBVisitRepository(context, table_name=table_name)


@pytest.fixture
def visit() -> Visit:
    """固定の訪問記録を提供する。"""
    return Visit(
        user_id="109876543210987654321",
        visit_id=UUID("019994f0-0000-7000-8000-000000000001"),
        prefecture=Prefecture.HOKKAIDO,
        created_at=datetime(2026, 9, 29, 13, 39, 42, tzinfo=UTC),
    )


@pytest.fixture
def second_visit(visit: Visit) -> Visit:
    """同じユーザーと都道府県で ID が異なる訪問記録を提供する。"""
    return replace(visit, visit_id=UUID("019994f0-0000-7000-8000-000000000002"))


@pytest.fixture
def other_user_visit(visit: Visit) -> Visit:
    """別ユーザーに属する同じ ID の訪問記録を提供する。"""
    return replace(visit, user_id="109876543210987654322")


@pytest.fixture(autouse=True)
def clean_visits(table, visit: Visit, second_visit: Visit, other_user_visit: Visit):
    """テストが使用する複合キーだけを実行前後に削除する。"""
    keys = [
        {"user_id": record.user_id, "visit_id": str(record.visit_id)}
        for record in (visit, second_visit, other_user_visit)
    ]
    for key in keys:
        table.delete_item(Key=key)
    try:
        yield
    finally:
        for key in keys:
            table.delete_item(Key=key)
