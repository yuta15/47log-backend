"""User activation endpoint DynamoDB Local integration fixtures."""

import os
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest

from src.functions.user_management.activate_user import dependencies
from src.modules.shared.infra.dynamodb import DynamoDBContext, DynamoDBSettings
from src.modules.shared.infra.utc_clock import UtcClock


@pytest.fixture(autouse=True)
def reset_usecase_cache() -> Iterator[None]:
    """依存のキャッシュをテスト前後に破棄する。"""
    dependencies._get_usecase.cache_clear()
    try:
        yield
    finally:
        dependencies._get_usecase.cache_clear()


@pytest.fixture
def now(monkeypatch: pytest.MonkeyPatch) -> datetime:
    """有効化処理の UTC 時刻を固定する。"""
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
def stored_user(table, stored_status: str) -> Iterator[dict[str, str]]:
    """指定状態のユーザーを登録し、終了後に削除する。"""
    item = {
        "user_id": "activate-endpoint-integration-user",
        "account_name": "dummy-account",
        "created_at": "2026-09-29T13:39:42+00:00",
        "updated_at": "2026-09-30T12:00:00+00:00",
        "status": stored_status,
    }
    try:
        table.put_item(Item=item)
        yield item
    finally:
        table.delete_item(Key={"user_id": item["user_id"]})


@pytest.fixture
def event(stored_user: dict[str, str]) -> dict:
    """本人の JWT claims と Body なしの HTTP API v2 イベントを提供する。"""
    return {
        "version": "2.0",
        "routeKey": "POST /users/me/activate",
        "rawPath": "/users/me/activate",
        "rawQueryString": "",
        "headers": {},
        "requestContext": {
            "stage": "$default",
            "http": {"method": "POST", "path": "/users/me/activate"},
            "authorizer": {"jwt": {"claims": {"sub": stored_user["user_id"]}}},
        },
        "body": None,
        "isBase64Encoded": False,
    }
