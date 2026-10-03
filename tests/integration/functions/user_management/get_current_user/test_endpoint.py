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


@pytest.mark.parametrize(
    ("stored_status", "expected_status_code"),
    [("DISABLED", 403), (None, 404)],
)
def test_handler_failure_returns_error_for_unavailable_user(
    event: dict,
    table,
    stored_user: dict[str, str],
    stored_status: str | None,
    expected_status_code: int,
) -> None:
    """DB の無効・未登録ユーザーに対して 403・404 とエラー JSON を返す。"""
    # Arrange
    if stored_status is None:
        table.delete_item(Key={"user_id": stored_user["user_id"]})
    else:
        table.put_item(Item={**stored_user, "status": stored_status})

    # Act
    response = handler.handler(event, None)

    # Assert
    assert response["statusCode"] == expected_status_code
    body = json.loads(response["body"])
    assert set(body) == {"message"}
    assert isinstance(body["message"], str)


@pytest.mark.parametrize("authenticated_user", ["stored_user", "other_user"])
def test_handler_success_returns_only_authenticated_user(
    event: dict,
    stored_user: dict[str, str],
    other_user: dict[str, str],
    authenticated_user: str,
) -> None:
    """複数ユーザーが存在しても認証 claims の sub に対応する本人の情報を返す。"""
    # Arrange
    user = {"stored_user": stored_user, "other_user": other_user}[authenticated_user]
    event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"] = user["user_id"]

    # Act
    response = handler.handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["accountName"] == user["account_name"]
