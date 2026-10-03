"""Current-user endpoint DynamoDB Local integration fixtures."""

import os
from collections.abc import Iterator

import pytest

from src.functions.user_management.get_current_user import dependencies
from src.modules.shared.infra.dynamodb import DynamoDBContext, DynamoDBSettings


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
def stored_user(table) -> Iterator[dict[str, str]]:
    """DynamoDB Local に有効ユーザーを登録し終了後に削除する。"""
    item = {
        "user_id": "endpoint-integration-user",
        "account_name": "dummy-account",
        "created_at": "2026-09-29T13:39:42+00:00",
        "updated_at": "2026-09-30T12:00:00+00:00",
        "status": "ENABLED",
    }
    dependencies._get_usecase.cache_clear()
    try:
        table.put_item(Item=item)
        yield item
    finally:
        dependencies._get_usecase.cache_clear()
        table.delete_item(Key={"user_id": item["user_id"]})


@pytest.fixture
def other_user(table, stored_user: dict[str, str]) -> Iterator[dict[str, str]]:
    """取得対象を区別できる別ユーザーを登録し終了後に削除する。"""
    item = {
        **stored_user,
        "user_id": "endpoint-integration-other-user",
        "account_name": "other-account",
    }
    try:
        table.put_item(Item=item)
        yield item
    finally:
        table.delete_item(Key={"user_id": item["user_id"]})


@pytest.fixture
def event(stored_user: dict[str, str]) -> dict:
    """登録したユーザーの JWT claims を持つ HTTP API v2 イベントを提供する。"""
    return {
        "version": "2.0",
        "routeKey": "GET /users/me",
        "rawPath": "/users/me",
        "rawQueryString": "",
        "headers": {},
        "requestContext": {
            "stage": "$default",
            "http": {"method": "GET", "path": "/users/me"},
            "authorizer": {"jwt": {"claims": {"sub": stored_user["user_id"]}}},
        },
        "body": None,
        "isBase64Encoded": False,
    }
