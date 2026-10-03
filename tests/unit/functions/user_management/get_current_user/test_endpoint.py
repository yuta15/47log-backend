"""Current-user endpoint HTTP response tests."""

import json
from unittest.mock import Mock

import pytest
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

from src.functions.user_management.get_current_user import endpoint
from src.modules.user_management.application import (
    UserForbiddenError,
    UserNotFoundError,
)


def test_get_current_user_success_returns_user_details(
    authentication: Mock,
    usecase: Mock,
) -> None:
    """認証済みユーザーの情報を 200 と camelCase・UTC 日時・Enum の JSON で返す。"""
    # Act
    response = endpoint.get_current_user()

    # Assert
    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert json.loads(response.body) == {
        "accountName": "dummy-account",
        "createdAt": "2026-09-29T13:39:42Z",
        "updatedAt": "2026-09-30T12:00:00Z",
        "status": "ENABLED",
    }


@pytest.mark.parametrize(
    ("error", "status_code", "message"),
    [
        (UserNotFoundError("private details"), 404, "User not found"),
        (UserForbiddenError("private details"), 403, "Forbidden"),
        (RuntimeError("private details"), 500, "Internal server error"),
    ],
)
def test_get_current_user_failure_returns_usecase_error_response(
    authentication: Mock,
    usecase: Mock,
    error: Exception,
    status_code: int,
    message: str,
) -> None:
    """Usecase の例外を所定のステータス・エラー JSON に変換し内部情報を公開しない。"""
    # Arrange
    usecase.execute.side_effect = error

    # Act
    response = endpoint.get_current_user()

    # Assert
    assert isinstance(response, Response)
    assert response.status_code == status_code
    assert response.content_type == "application/json"
    assert json.loads(response.body) == {"message": message}


def test_get_current_user_failure_returns_unauthorized_response(
    authentication: Mock,
    usecase: Mock,
) -> None:
    """認証情報取得のエラーを 401 と所定のエラー JSON に変換する。"""
    # Arrange
    authentication.side_effect = UnauthorizedError("private details")

    # Act
    response = endpoint.get_current_user()

    # Assert
    assert isinstance(response, Response)
    assert response.status_code == 401
    assert response.content_type == "application/json"
    assert json.loads(response.body) == {"message": "Unauthorized"}
    usecase.execute.assert_not_called()
