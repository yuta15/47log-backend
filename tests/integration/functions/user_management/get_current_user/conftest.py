"""Current-user endpoint DynamoDB Local integration fixtures."""

import os
from collections.abc import Iterator

import pytest

from src.functions.user_management.get_current_user import dependencies
from src.modules.shared.infra.dynamodb import DynamoDBContext, DynamoDBSettings


@pytest.fixture
def stored_user(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, str]]:
    """DynamoDB Local に有効ユーザーを登録し終了後に削除する。"""
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL", "http://localhost:8000")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "local")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "local")
    monkeypatch.setenv("AWS_REGION", "ap-northeast-1")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_URL", endpoint_url)
    context = DynamoDBContext(DynamoDBSettings())
    table = context.resource.Table(os.environ.get("USERS_TABLE_NAME", "users_table"))
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
