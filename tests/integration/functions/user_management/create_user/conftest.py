"""User registration endpoint DynamoDB Local integration fixtures."""

import json
import os
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest

from src.functions.user_management.create_user import dependencies
from src.modules.shared.infra.dynamodb import DynamoDBContext, DynamoDBSettings
from src.modules.shared.infra.utc_clock import UtcClock


@pytest.fixture(autouse=True)
def reset_usecase_cache() -> Iterator[None]:
    """キャッシュした DB 接続がテスト間に残らないようにする。"""
    dependencies._get_usecase.cache_clear()
    try:
        yield
    finally:
        dependencies._get_usecase.cache_clear()


@pytest.fixture
def created_at(monkeypatch: pytest.MonkeyPatch) -> datetime:
    """登録処理の UTC 時刻を固定する。"""
    now = datetime(2026, 10, 4, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(UtcClock, "now", lambda self: now)
    return now


@pytest.fixture
def table(monkeypatch: pytest.MonkeyPatch):
    """DynamoDB Local の users テーブルを提供する。"""
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL", "http://localhost:8000")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "local")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "local")
    monkeypatch.setenv("AWS_REGION", "ap-northeast-1")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_URL", endpoint_url)
    context = DynamoDBContext(DynamoDBSettings())
    return context.resource.Table(os.environ.get("USERS_TABLE_NAME", "users_table"))


@pytest.fixture
def user_id(table) -> Iterator[str]:
    """登録対象の固定ユーザー ID をテスト前後に削除する。"""
    user_id = "create-endpoint-integration-user"
    key = {"user_id": user_id}
    table.delete_item(Key=key)
    try:
        yield user_id
    finally:
        table.delete_item(Key=key)


@pytest.fixture
def other_user_id(table) -> Iterator[str]:
    """別ユーザーの固定 ID をテスト前後に削除する。"""
    user_id = "create-endpoint-integration-other-user"
    key = {"user_id": user_id}
    table.delete_item(Key=key)
    try:
        yield user_id
    finally:
        table.delete_item(Key=key)


@pytest.fixture
def stored_user(table, user_id: str) -> dict[str, str]:
    """作成・更新日時の異なる既存ユーザーを登録する。"""
    item = {
        "user_id": user_id,
        "account_name": "original-account",
        "created_at": "2026-09-29T13:39:42+00:00",
        "updated_at": "2026-09-30T12:00:00+00:00",
        "status": "ENABLED",
    }
    table.put_item(Item=item)
    return item


@pytest.fixture
def event(user_id: str, created_at: datetime) -> dict:
    """未登録の本人と有効な Body を持つ HTTP API v2 イベントを提供する。"""
    return {
        "version": "2.0",
        "routeKey": "POST /users",
        "rawPath": "/users",
        "rawQueryString": "",
        "headers": {"content-type": "application/json"},
        "requestContext": {
            "stage": "$default",
            "http": {"method": "POST", "path": "/users"},
            "authorizer": {"jwt": {"claims": {"sub": user_id}}},
        },
        "body": json.dumps({"accountName": "dummy-account"}),
        "isBase64Encoded": False,
    }
