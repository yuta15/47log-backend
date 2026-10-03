"""Current-user status endpoint DynamoDB Local integration fixtures."""

import os
from collections.abc import Iterator

import pytest

from src.functions.user_management.get_current_user_status import dependencies
from src.modules.shared.infra.dynamodb import DynamoDBContext, DynamoDBSettings


@pytest.fixture(autouse=True)
def reset_usecase_cache() -> Iterator[None]:
    """キャッシュした DB 接続がテスト間に残らないようにする。"""
    dependencies._get_usecase.cache_clear()
    try:
        yield
    finally:
        dependencies._get_usecase.cache_clear()


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
    """テスト前後に削除する固定のユーザー ID を提供する。"""
    user_id = "status-endpoint-integration-user"
    key = {"user_id": user_id}
    table.delete_item(Key=key)
    try:
        yield user_id
    finally:
        table.delete_item(Key=key)


@pytest.fixture
def stored_user(table, user_id: str) -> dict[str, str]:
    """有効ユーザーを登録し user_id fixture で終了後に削除する。"""
    item = {
        "user_id": user_id,
        "account_name": "dummy-account",
        "created_at": "2026-09-29T13:39:42+00:00",
        "updated_at": "2026-09-30T12:00:00+00:00",
        "status": "ENABLED",
    }
    table.put_item(Item=item)
    return item


@pytest.fixture
def other_user(table, stored_user: dict[str, str]) -> Iterator[dict[str, str]]:
    """取得対象を区別できる無効ユーザーを登録し終了後に削除する。"""
    item = {
        **stored_user,
        "user_id": "status-endpoint-integration-other-user",
        "account_name": "other-account",
        "status": "DISABLED",
    }
    try:
        table.put_item(Item=item)
        yield item
    finally:
        table.delete_item(Key={"user_id": item["user_id"]})


@pytest.fixture
def event(user_id: str) -> dict:
    """固定ユーザーの JWT claims を持つ HTTP API v2 イベントを提供する。"""
    return {
        "version": "2.0",
        "routeKey": "GET /users/me/status",
        "rawPath": "/users/me/status",
        "rawQueryString": "",
        "headers": {},
        "requestContext": {
            "stage": "$default",
            "http": {"method": "GET", "path": "/users/me/status"},
            "authorizer": {"jwt": {"claims": {"sub": user_id}}},
        },
        "body": None,
        "isBase64Encoded": False,
    }
