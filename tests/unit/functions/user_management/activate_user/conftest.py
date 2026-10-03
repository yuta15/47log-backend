"""User activation endpoint unit test fixtures."""

from unittest.mock import Mock

import pytest
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2

from src.functions.auth.models import AuthClaims
from src.functions.user_management.activate_user import endpoint
from src.modules.user_management.application import ActivateUserUsecase


@pytest.fixture
def auth_claims() -> AuthClaims:
    """認証済みの固定ユーザーを提供する。"""
    return AuthClaims(sub="user-1")


@pytest.fixture
def authentication(auth_claims: AuthClaims, monkeypatch: pytest.MonkeyPatch) -> Mock:
    """認証情報取得を差し替え、エンドポイントを直接呼べるようにする。"""
    event = APIGatewayProxyEventV2({})
    monkeypatch.setattr(endpoint, "router", Mock(current_event=event))
    authentication = Mock(return_value=auth_claims)
    monkeypatch.setattr(endpoint, "get_auth_claims", authentication)
    return authentication


@pytest.fixture
def usecase(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Usecase を差し替え外部サービスへの接続を避ける。"""
    usecase = Mock(spec=ActivateUserUsecase)
    usecase.execute.return_value = None
    monkeypatch.setattr(endpoint, "_get_usecase", Mock(return_value=usecase))
    return usecase
