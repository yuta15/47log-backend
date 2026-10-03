"""User registration endpoint HTTP response tests."""

import json
from unittest.mock import Mock

import pytest
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

from src.functions.auth.models import AuthClaims
from src.functions.user_management.create_user import endpoint
from src.modules.user_management.application import UserAlreadyExistsError
from src.modules.user_management.domain import UserIdVo
from src.modules.user_management.domain.entities.value_objects import AccountNameVo


def test_create_user_success_returns_created_without_body(
    authentication: Mock,
    auth_claims: AuthClaims,
    usecase: Mock,
) -> None:
    """JWT の sub とリクエストの名前で登録し本文なしの 201 を返す。"""
    # Act
    response = endpoint.create_user()

    # Assert
    assert response.status_code == 201
    assert response.body in (None, "")
    usecase.execute.assert_called_once_with(
        UserIdVo(auth_claims.sub), AccountNameVo("dummy-account")
    )


@pytest.mark.parametrize("request_body", ['{"accountName": ""}'], indirect=True)
def test_create_user_failure_rejects_invalid_request(
    authentication: Mock,
    usecase: Mock,
) -> None:
    """入力検証の失敗を 400 に変換し登録処理を呼ばない。"""
    # Act
    response = endpoint.create_user()

    # Assert
    assert response.status_code == 400
    assert response.content_type == "application/json"
    body = json.loads(response.body)
    assert set(body) == {"message"}
    assert isinstance(body["message"], str)
    usecase.execute.assert_not_called()


@pytest.mark.parametrize("request_body", [None, "", "{"], indirect=True)
def test_create_user_failure_rejects_missing_or_malformed_json(
    authentication: Mock,
    usecase: Mock,
) -> None:
    """Body の欠落・JSON 解析失敗を 400 に変換し登録処理を呼ばない。"""
    # Act
    response = endpoint.create_user()

    # Assert
    assert response.status_code == 400
    assert response.content_type == "application/json"
    body = json.loads(response.body)
    assert set(body) == {"message"}
    assert isinstance(body["message"], str)
    usecase.execute.assert_not_called()


def test_create_user_failure_returns_unauthorized_response(
    authentication: Mock,
    usecase: Mock,
) -> None:
    """認証エラーを 401 に変換し登録処理を呼ばない。"""
    # Arrange
    authentication.side_effect = UnauthorizedError("private details")

    # Act
    response = endpoint.create_user()

    # Assert
    assert response.status_code == 401
    assert response.content_type == "application/json"
    body = json.loads(response.body)
    assert set(body) == {"message"}
    assert isinstance(body["message"], str)
    assert "private details" not in body["message"]
    usecase.execute.assert_not_called()


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (UserAlreadyExistsError("private details"), 409),
        (RuntimeError("private details"), 500),
    ],
)
def test_create_user_failure_returns_usecase_error_response(
    authentication: Mock,
    usecase: Mock,
    error: Exception,
    status_code: int,
) -> None:
    """登録の競合・想定外例外を 409・500 に変換し内部情報を公開しない。"""
    # Arrange
    usecase.execute.side_effect = error

    # Act
    response = endpoint.create_user()

    # Assert
    assert response.status_code == status_code
    assert response.content_type == "application/json"
    body = json.loads(response.body)
    assert set(body) == {"message"}
    assert isinstance(body["message"], str)
    assert "private details" not in body["message"]
