"""Current-user handler tests."""

import json
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from src.functions import get_current_user
from src.modules.user_management.application import (
    GetCurrentUserOutput,
    GetCurrentUserUsecase,
    UserForbiddenError,
    UserNotFoundError,
    UserRepositoryError,
)
from src.modules.user_management.domain import UserIdVo, UserStatus

USER_ID = "user-1"


@pytest.fixture
def event() -> dict:
    """検証済み JWT の subject を含むイベントを提供する。"""
    return {"requestContext": {"authorizer": {"jwt": {"claims": {"sub": USER_ID}}}}}


@pytest.fixture
def usecase(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """固定の返却値を持つユースケースに差し替える。"""
    usecase = Mock(spec=GetCurrentUserUsecase)
    usecase.execute.return_value = GetCurrentUserOutput(
        account_name="dummy-account",
        created_at=datetime(2026, 9, 29, 13, 39, 42, tzinfo=UTC),
        updated_at=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
        status=UserStatus.ENABLED,
    )
    monkeypatch.setattr(get_current_user, "_get_usecase", Mock(return_value=usecase))
    return usecase


def test_handler_success_returns_user_details(event: dict, usecase: Mock) -> None:
    """認証済み ID を渡して日時と Enum を JSON に変換することを確認する。"""
    # Arrange
    event["body"] = json.dumps({"user_id": "another-user"})
    event["queryStringParameters"] = {"user_id": "another-user"}

    # Act
    response = get_current_user.handler(event, None)

    # Assert
    usecase.execute.assert_called_once_with(UserIdVo(USER_ID))
    assert response["statusCode"] == 200
    assert response["headers"] == {"Content-Type": "application/json"}
    assert response["isBase64Encoded"] is False
    assert json.loads(response["body"]) == {
        "account_name": "dummy-account",
        "created_at": "2026-09-29T13:39:42Z",
        "updated_at": "2026-09-30T12:00:00Z",
        "status": "ENABLED",
    }


def test_handler_success_accepts_additional_auth_claims(
    event: dict, usecase: Mock
) -> None:
    """JWT の追加 claims を許容し sub だけをユーザー ID に使うことを確認する。"""
    # Arrange
    event["requestContext"]["authorizer"]["jwt"]["claims"].update(
        {"iss": "https://issuer.example", "aud": "client-id", "exp": 1791000000}
    )

    # Act
    response = get_current_user.handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    usecase.execute.assert_called_once_with(UserIdVo(USER_ID))


@pytest.mark.parametrize(
    "event",
    [
        {},
        {"requestContext": None},
        {"requestContext": {"authorizer": None}},
        {"requestContext": {"authorizer": {"jwt": None}}},
        {"requestContext": {"authorizer": {"jwt": {"claims": []}}}},
        {"requestContext": {"authorizer": {"jwt": {"claims": {}}}}},
    ],
)
def test_handler_failure_rejects_missing_authentication(
    event: dict, usecase: Mock
) -> None:
    """認証情報が不正な場合に body の ID へフォールバックしないことを確認する。"""
    # Arrange
    event["body"] = json.dumps({"user_id": USER_ID})

    # Act
    response = get_current_user.handler(event, None)

    # Assert
    assert response["statusCode"] == 401
    usecase.execute.assert_not_called()
    get_current_user._get_usecase.assert_not_called()


@pytest.mark.parametrize("subject", [None, "", "  ", 123, "a" * 256])
def test_handler_failure_rejects_invalid_subject(
    event: dict, usecase: Mock, subject: object
) -> None:
    """subject の必須・型・空文字・長さの検証に失敗すると 401 になることを確認する。"""
    # Arrange
    event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"] = subject

    # Act
    response = get_current_user.handler(event, None)

    # Assert
    assert response["statusCode"] == 401
    usecase.execute.assert_not_called()


@pytest.mark.parametrize(
    ("error", "status_code", "message"),
    [
        (UserNotFoundError("private details"), 404, "User not found"),
        (UserForbiddenError("private details"), 403, "Forbidden"),
        (UserRepositoryError("private details"), 500, "Internal server error"),
        (RuntimeError("private details"), 500, "Internal server error"),
    ],
)
def test_handler_failure_maps_usecase_errors(
    event: dict, usecase: Mock, error: Exception, status_code: int, message: str
) -> None:
    """ユースケースの例外を HTTP に変換し内部情報を公開しないことを確認する。"""
    # Arrange
    usecase.execute.side_effect = error

    # Act
    response = get_current_user.handler(event, None)

    # Assert
    assert response["statusCode"] == status_code
    assert json.loads(response["body"]) == {"message": message}


def test_handler_failure_returns_internal_error_when_dependencies_fail(
    event: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    """依存の初期化に失敗した場合も 500 を返すことを確認する。"""
    # Arrange
    monkeypatch.setattr(
        get_current_user, "_get_usecase", Mock(side_effect=RuntimeError("private"))
    )

    # Act
    response = get_current_user.handler(event, None)

    # Assert
    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"message": "Internal server error"}


@pytest.mark.parametrize(
    ("table_name", "expected"),
    [(None, "users_table"), ("custom-users", "custom-users")],
)
def test_handler_success_uses_configured_repository_and_reuses_dependencies(
    event: dict, monkeypatch: pytest.MonkeyPatch, table_name: str | None, expected: str
) -> None:
    """実際の依存を接続し設定したテーブルを使い次回も再利用することを確認する。"""
    # Arrange
    if table_name is None:
        monkeypatch.delenv("USERS_TABLE_NAME", raising=False)
    else:
        monkeypatch.setenv("USERS_TABLE_NAME", table_name)
    resource = Mock()
    resource.Table.return_value.get_item.return_value = {
        "Item": {
            "user_id": USER_ID,
            "account_name": "dummy-account",
            "created_at": "2026-09-29T13:39:42+00:00",
            "updated_at": "2026-09-30T12:00:00+00:00",
            "status": "ENABLED",
        }
    }
    create_resource = Mock(return_value=resource)
    monkeypatch.setattr("boto3.resource", create_resource)
    get_current_user._get_usecase.cache_clear()

    try:
        # Act
        first = get_current_user.handler(event, None)
        second = get_current_user.handler(event, None)

        # Assert
        assert first["statusCode"] == second["statusCode"] == 200
        resource.Table.assert_called_once_with(expected)
        create_resource.assert_called_once()
        resource.Table.return_value.get_item.assert_called_with(
            Key={"user_id": USER_ID}, ConsistentRead=True
        )
    finally:
        get_current_user._get_usecase.cache_clear()
