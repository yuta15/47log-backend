"""User registration integration tests through the actual Lambda entrypoint."""

import json
from datetime import datetime

import pytest

from src.functions import handler

pytestmark = pytest.mark.integration


def test_handler_success_persists_enabled_user(
    event: dict, table, user_id: str, created_at: datetime
) -> None:
    """本人を有効状態・同じ作成更新日時で保存し本文なしの 201 を返す。"""
    # Act
    response = handler.handler(event, None)
    item = table.get_item(Key={"user_id": user_id}, ConsistentRead=True).get("Item")

    # Assert
    assert response["statusCode"] == 201
    assert response.get("body") in (None, "")
    assert item == {
        "user_id": user_id,
        "account_name": "dummy-account",
        "status": "ENABLED",
        "created_at": created_at.isoformat(),
        "updated_at": created_at.isoformat(),
    }


@pytest.mark.parametrize("status", ["ENABLED", "DISABLED"])
def test_handler_failure_preserves_existing_user_on_conflict(
    event: dict, table, stored_user: dict[str, str], status: str
) -> None:
    """既存ユーザーの状態にかかわらず再登録は 409 となり全保存値を維持する。"""
    # Arrange
    original = {**stored_user, "status": status}
    table.put_item(Item=original)

    # Act
    response = handler.handler(event, None)
    item = table.get_item(
        Key={"user_id": stored_user["user_id"]}, ConsistentRead=True
    ).get("Item")

    # Assert
    assert response["statusCode"] == 409
    assert item == original


def test_handler_failure_rejects_repeated_registration(
    event: dict, table, user_id: str
) -> None:
    """初回登録は 201、再送は 409 となり初回の保存値を維持する。"""
    # Arrange
    first_response = handler.handler(event, None)
    first_item = table.get_item(Key={"user_id": user_id}, ConsistentRead=True).get(
        "Item"
    )
    event["body"] = json.dumps({"accountName": "different-account"})

    # Act
    response = handler.handler(event, None)
    item = table.get_item(Key={"user_id": user_id}, ConsistentRead=True).get("Item")

    # Assert
    assert first_response["statusCode"] == 201
    assert response["statusCode"] == 409
    assert item == first_item


def test_handler_success_allows_same_account_name_for_different_users(
    event: dict, table, user_id: str, other_user_id: str
) -> None:
    """別の JWT sub なら同じ accountName でもそれぞれ 201 で登録できる。"""
    # Arrange
    first_response = handler.handler(event, None)
    event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"] = other_user_id

    # Act
    response = handler.handler(event, None)

    # Assert
    assert first_response["statusCode"] == 201
    assert response["statusCode"] == 201
    for subject in (user_id, other_user_id):
        item = table.get_item(Key={"user_id": subject}, ConsistentRead=True).get("Item")
        assert item is not None
        assert item["user_id"] == subject
        assert item["account_name"] == "dummy-account"


@pytest.mark.parametrize(
    "request_body",
    [
        None,
        "{",
        "[]",
        "{}",
        '{"accountName": ""}',
        '{"accountName": "valid-name", "status": "DISABLED"}',
        '{"accountName": "valid-name", "extra": "value"}',
    ],
)
def test_handler_failure_does_not_persist_invalid_request(
    event: dict, table, user_id: str, request_body: str | None
) -> None:
    """不正 Body を 400 とエラー JSON に変換しユーザーを作成しない。"""
    # Arrange
    event["body"] = request_body

    # Act
    response = handler.handler(event, None)
    item = table.get_item(Key={"user_id": user_id}, ConsistentRead=True)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert set(body) == {"message"}
    assert isinstance(body["message"], str)
    assert "Item" not in item


def test_handler_failure_rejects_user_id_in_body(
    event: dict, table, user_id: str, other_user_id: str
) -> None:
    """Body に userId を指定すると 400 となり本人・指定先とも作成されない。"""
    # Arrange
    event["body"] = json.dumps({"accountName": "valid-name", "userId": other_user_id})

    # Act
    response = handler.handler(event, None)

    # Assert
    assert response["statusCode"] == 400
    for subject in (user_id, other_user_id):
        assert "Item" not in table.get_item(
            Key={"user_id": subject}, ConsistentRead=True
        )


@pytest.mark.parametrize("auth_context", [None, {"jwt": {"claims": {}}}])
def test_handler_failure_does_not_register_unauthenticated_user(
    event: dict, table, user_id: str, auth_context: dict | None
) -> None:
    """認証情報・sub の欠落を 401 に変換しユーザーを作成しない。"""
    # Arrange
    event["requestContext"]["authorizer"] = auth_context

    # Act
    response = handler.handler(event, None)

    # Assert
    assert response["statusCode"] == 401
    assert "Item" not in table.get_item(Key={"user_id": user_id}, ConsistentRead=True)
