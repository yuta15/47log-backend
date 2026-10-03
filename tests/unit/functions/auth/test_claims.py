"""JWT claims extraction tests."""

import pytest
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2

from src.functions.auth import claims
from src.functions.auth.models import AuthClaims


def test_get_auth_claims_success_returns_subject() -> None:
    """追加 claims を許容し sub を検証済みの認証情報として返す。"""
    event = APIGatewayProxyEventV2(
        {
            "requestContext": {
                "authorizer": {"jwt": {"claims": {"sub": "user-1", "aud": "client-id"}}}
            }
        }
    )

    # Act
    actual = claims.get_auth_claims(event)

    # Assert
    assert isinstance(actual, AuthClaims)
    assert actual.sub == "user-1"


@pytest.mark.parametrize(
    "auth_context",
    [
        {},
        {"authorizer": None},
        {"authorizer": {}},
        {"authorizer": {"jwt": None}},
        {"authorizer": {"jwt": {"claims": {}}}},
        {"authorizer": {"jwt": {"claims": {"sub": 123}}}},
    ],
)
def test_get_auth_claims_failure_rejects_missing_or_invalid_subject(
    auth_context: dict,
) -> None:
    """sub の欠落・代表的な不正値を認証エラーに変換する。"""
    event = APIGatewayProxyEventV2({"requestContext": auth_context})

    with pytest.raises(UnauthorizedError):
        claims.get_auth_claims(event)
