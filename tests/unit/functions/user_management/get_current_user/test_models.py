"""Current-user response model serialization tests."""

import json

from src.functions.user_management.get_current_user.models import GetCurrentUserResponse
from src.modules.user_management.application import GetCurrentUserOutput


def test_get_current_user_response_success_serializes_api_contract(
    output: GetCurrentUserOutput,
) -> None:
    """取得結果を camelCase のキー・UTC 日時・Enum の値でシリアライズする。"""
    # Act
    response = GetCurrentUserResponse.model_validate(output)
    actual = json.loads(response.model_dump_json(by_alias=True))

    # Assert
    assert actual == {
        "accountName": "dummy-account",
        "createdAt": "2026-09-29T13:39:42Z",
        "updatedAt": "2026-09-30T12:00:00Z",
        "status": "ENABLED",
    }
