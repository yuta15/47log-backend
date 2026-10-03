"""Current-user status integration tests through the actual Lambda entrypoint."""

import json

import pytest

from src.functions import handler

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    ("stored_status", "expected_status"),
    [("ENABLED", "ENABLED"), ("DISABLED", "DISABLED"), (None, "UNREGISTERED")],
)
def test_handler_success_returns_current_user_status(
    event: dict,
    table,
    stored_user: dict[str, str],
    stored_status: str | None,
    expected_status: str,
) -> None:
    """DB の有効・無効・未登録ユーザーに対して 200 と対応する状態を返す。"""
    # Arrange
    if stored_status is None:
        table.delete_item(Key={"user_id": stored_user["user_id"]})
    else:
        table.put_item(Item={**stored_user, "status": stored_status})

    # Act
    response = handler.handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"
    assert json.loads(response["body"]) == {"status": expected_status}


@pytest.mark.parametrize("authenticated_user", ["stored_user", "other_user"])
def test_handler_success_returns_only_authenticated_user_status(
    event: dict,
    stored_user: dict[str, str],
    other_user: dict[str, str],
    authenticated_user: str,
) -> None:
    """状態が異なる複数ユーザーが存在しても認証された本人の状態を返す。"""
    # Arrange
    user = {"stored_user": stored_user, "other_user": other_user}[authenticated_user]
    event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"] = user["user_id"]

    # Act
    response = handler.handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"status": user["status"]}


def test_handler_success_does_not_create_unregistered_user(
    event: dict,
    table,
    user_id: str,
) -> None:
    """未登録ユーザーの状態を取得しても DB にユーザーを作成しない。"""
    # Act
    response = handler.handler(event, None)
    item = table.get_item(Key={"user_id": user_id}, ConsistentRead=True)

    # Assert
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"status": "UNREGISTERED"}
    assert "Item" not in item
