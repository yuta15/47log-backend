"""User value object tests."""

from dataclasses import FrozenInstanceError

import pytest

from src.modules.user_management.domain.entities.value_objects import (
    AccountNameVo,
    UserIdVo,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("a", "a"),
        ("109876543210987654321", "109876543210987654321"),
        (
            "ed9affb2-b079-4be9-9cdd-2f0c77f387ca",
            "ed9affb2-b079-4be9-9cdd-2f0c77f387ca",
        ),
        ("Provider|AbC-123_:@/", "Provider|AbC-123_:@/"),
        ("ユーザーＡ", "ユーザーＡ"),
        ("a b\nc", "a b\nc"),
        (" \tAbC\r\n", "AbC"),
        ("\u3000AbC\u3000", "AbC"),
        ("a" * 255, "a" * 255),
        ("  " + "a" * 255 + "  ", "a" * 255),
    ],
)
def test_user_id_vo_success_trims_and_preserves_identifier(
    value: str, expected: str
) -> None:
    """前後のみ trim し、UUID に限らない文字列と255文字の境界値を保持する。"""
    # Act
    user_id = UserIdVo(value)

    # Assert
    assert user_id.value == expected


@pytest.mark.parametrize(
    "value", ["", " \t\r\n", "\u3000", "a" * 256, "  " + "a" * 256 + "  "]
)
def test_user_id_vo_failure_rejects_empty_or_too_long_identifier(value: str) -> None:
    """trim 後に空文字または256文字以上になる ID を拒否する。"""
    # Assert
    with pytest.raises(ValueError):
        UserIdVo(value)


@pytest.mark.parametrize("value", [None, 123, True, b"subject", ["subject"]])
def test_user_id_vo_failure_rejects_non_string_values(value) -> None:
    """文字列以外の ID を暗黙変換せず拒否する。"""
    # Assert
    with pytest.raises(ValueError):
        UserIdVo(value)


def test_user_id_vo_failure_prevents_value_mutation() -> None:
    """生成済みの ID を変更できないことを確認する。"""
    # Arrange
    user_id = UserIdVo("original-subject")

    # Assert
    with pytest.raises(FrozenInstanceError):
        user_id.value = "different-subject"


@pytest.mark.parametrize("value", ["a", "0", "Az09", "a-_z", "a" * 64])
def test_account_name_vo_success_accepts_valid_names(value: str) -> None:
    """許可文字と1文字・64文字の境界値を受け入れることを確認する。"""
    # Act
    account_name = AccountNameVo(value)

    # Assert
    assert account_name.value == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "a" * 65,
        "-abc",
        "_abc",
        "abc-",
        "abc_",
        "-",
        "_",
        "a b",
        "a.b",
        "a\nb",
        "abc\n",
        "あいう",
        "\uff21bc",
        "a\uff11b",
        None,
        123,
    ],
)
def test_account_name_vo_failure_rejects_invalid_names(value) -> None:
    """長さ・先頭末尾・許可文字・文字列型の制約違反を拒否することを確認する。"""
    # Assert
    with pytest.raises(ValueError):
        AccountNameVo(value)
