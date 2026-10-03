"""Current-user status endpoint HTTP response tests."""

import json
from unittest.mock import Mock

import pytest
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

from src.functions.auth.models import AuthClaims
from src.functions.user_management.get_current_user_status import endpoint
from src.modules.user_management.application import (
    CurrentUserStatus,
    GetCurrentUserStatusOutput,
)
from src.modules.user_management.domain import UserIdVo


@pytest.mark.parametrize("status", ["ENABLED", "DISABLED", "UNREGISTERED"])
def test_get_current_user_status_success_returns_status(
    authentication: Mock,
    auth_claims: AuthClaims,
    usecase: Mock,
    status: str,
) -> None:
    """有効・無効・未登録のいずれも 200 と status のみの JSON を返す。"""
    # Arrange
    usecase.execute.return_value = GetCurrentUserStatusOutput(
        status=CurrentUserStatus(status)
    )

    # Act
    response = endpoint.get_current_user_status()

    # Assert
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert json.loads(response.body) == {"status": status}
    usecase.execute.assert_called_once_with(UserIdVo(auth_claims.sub))


def test_get_current_user_status_failure_returns_unauthorized_response(
    authentication: Mock,
    usecase: Mock,
) -> None:
    """認証エラーを 401 とエラー JSON に変換しユーザー取得処理を呼ばない。"""
    # Arrange
    authentication.side_effect = UnauthorizedError("private details")

    # Act
    response = endpoint.get_current_user_status()

    # Assert
    assert response.status_code == 401
    assert response.content_type == "application/json"
    body = json.loads(response.body)
    assert set(body) == {"message"}
    assert isinstance(body["message"], str)
    assert "private details" not in body["message"]
    usecase.execute.assert_not_called()


def test_get_current_user_status_failure_returns_internal_error_response(
    authentication: Mock,
    usecase: Mock,
) -> None:
    """ユーザー取得中の例外を 500 とエラー JSON に変換し内部情報を公開しない。"""
    # Arrange
    usecase.execute.side_effect = RuntimeError("private details")

    # Act
    response = endpoint.get_current_user_status()

    # Assert
    assert response.status_code == 500
    assert response.content_type == "application/json"
    body = json.loads(response.body)
    assert set(body) == {"message"}
    assert isinstance(body["message"], str)
    assert "private details" not in body["message"]
