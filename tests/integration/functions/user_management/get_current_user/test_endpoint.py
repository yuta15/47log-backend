"""Current-user endpoint integration test through the actual Lambda entrypoint."""

import json

import pytest

from src.functions import handler

pytestmark = pytest.mark.integration


def test_handler_success_returns_stored_user(event: dict) -> None:
    """共通ハンドラーから DB の有効ユーザーを取得し 200 と所定の JSON を返す。"""
    # Act
    response = handler.handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {
        "accountName": "dummy-account",
        "createdAt": "2026-09-29T13:39:42Z",
        "updatedAt": "2026-09-30T12:00:00Z",
        "status": "ENABLED",
    }
