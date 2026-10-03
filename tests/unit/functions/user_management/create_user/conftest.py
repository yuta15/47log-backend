"""User registration endpoint unit test fixtures."""

import json
from unittest.mock import Mock

import pytest
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2

from src.functions.auth.models import AuthClaims
from src.functions.user_management.create_user import endpoint
from src.modules.user_management.application import CreateUserUsecase


@pytest.fixture
def request_body(request: pytest.FixtureRequest) -> str | None:
    """指定された Body、または有効な登録リクエスト JSON を提供する。"""
    return getattr(request, "param", json.dumps({"accountName": "dummy-account"}))


@pytest.fixture
def auth_claims() -> AuthClaims:
    """認証済みの固定ユーザーを提供する。"""
    return AuthClaims(sub="user-1")


@pytest.fixture
def authentication(
    auth_claims: AuthClaims, request_body: str | None, monkeypatch: pytest.MonkeyPatch
) -> Mock:
    """認証情報と Router を差し替えてリクエスト Body をエンドポイントに渡す。"""
    event = APIGatewayProxyEventV2({"body": request_body, "isBase64Encoded": False})
    monkeypatch.setattr(endpoint, "router", Mock(current_event=event))
    authentication = Mock(return_value=auth_claims)
    monkeypatch.setattr(endpoint, "get_auth_claims", authentication)
    return authentication


@pytest.fixture
def usecase(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """登録 Usecase を差し替えて外部サービスへの接続を避ける。"""
    usecase = Mock(spec=CreateUserUsecase)
    usecase.execute.return_value = None
    monkeypatch.setattr(endpoint, "_get_usecase", Mock(return_value=usecase))
    return usecase
