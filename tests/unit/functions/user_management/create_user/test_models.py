"""User registration request model validation tests."""

import pytest
from pydantic import ValidationError

from src.functions.user_management.create_user.models import CreateUserRequest


@pytest.mark.parametrize("account_name", ["a", "0", "Az09", "a-_z", "a" * 64])
def test_create_user_request_success_accepts_valid_account_name(
    account_name: str,
) -> None:
    """accountName の許可文字と1文字・64文字の境界値を受け付け値を保持する。"""
    # Act
    request = CreateUserRequest.model_validate({"accountName": account_name})

    # Assert
    assert request.account_name == account_name


@pytest.mark.parametrize(
    "account_name",
    [
        None,
        123,
        True,
        [],
        {},
        "",
        "a" * 65,
        "-abc",
        "_abc",
        "abc-",
        "abc_",
        "a b",
        " abc ",
        "a.b",
        "abc\n",
        "あいう",
        "\uff21bc",
    ],
)
def test_create_user_request_failure_rejects_invalid_account_name(
    account_name: object,
) -> None:
    """文字列以外・長さ・許可文字・先頭末尾の制約違反を暗黙変換せず拒否する。"""
    with pytest.raises(ValidationError):
        CreateUserRequest.model_validate({"accountName": account_name})


@pytest.mark.parametrize(
    "body", [None, [], "account", 123, {}, {"account_name": "valid-name"}]
)
def test_create_user_request_failure_rejects_invalid_shape_or_missing_account_name(
    body: object,
) -> None:
    """オブジェクト以外の入力と契約上必須の accountName の欠落を拒否する。"""
    with pytest.raises(ValidationError):
        CreateUserRequest.model_validate(body)


@pytest.mark.parametrize(
    ("key", "value"),
    [("userId", "other-user"), ("status", "DISABLED"), ("extra", "value")],
)
def test_create_user_request_failure_rejects_extra_fields(key: str, value: str) -> None:
    """userId・status を含め契約外の Body 項目を拒否する。"""
    with pytest.raises(ValidationError):
        CreateUserRequest.model_validate({"accountName": "valid-name", key: value})
