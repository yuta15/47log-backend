"""User deactivation endpoint HTTP response tests."""

from unittest.mock import Mock

import pytest
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

from src.functions.auth.models import AuthClaims
from src.functions.user_management.deactivate_user import endpoint
from src.modules.user_management.application import UserNotFoundError
from src.modules.user_management.domain import UserIdVo


def test_deactivate_user_success_returns_no_content(
    authentication: Mock, auth_claims: AuthClaims, usecase: Mock
) -> None:
    """JWT の sub を Usecase に渡し、204 と空の本文を返す。"""
    # Act
    response = endpoint.deactivate_user()

    # Assert
    usecase.execute.assert_called_once_with(UserIdVo(auth_claims.sub))
    assert response.status_code == 204
    assert response.body in (None, "")


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (UserNotFoundError("private details"), 404),
        (RuntimeError("private details"), 500),
    ],
)
def test_deactivate_user_failure_converts_usecase_error(
    authentication: Mock, usecase: Mock, error: Exception, status_code: int
) -> None:
    """Usecase の例外を 404・500 に変換し、内部の例外詳細を公開しない。"""
    # Arrange
    usecase.execute.side_effect = error

    # Act
    response = endpoint.deactivate_user()

    # Assert
    assert response.status_code == status_code
    assert "private details" not in (response.body or "")


def test_deactivate_user_failure_returns_unauthorized(
    authentication: Mock, usecase: Mock
) -> None:
    """認証エラーを 401 に変換し、Usecase を呼ばない。"""
    # Arrange
    authentication.side_effect = UnauthorizedError("private details")

    # Act
    response = endpoint.deactivate_user()

    # Assert
    assert response.status_code == 401
    usecase.execute.assert_not_called()
