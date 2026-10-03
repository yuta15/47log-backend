"""User deactivation through the actual Lambda entrypoint and DynamoDB Local."""

from datetime import datetime

import pytest

from src.functions import handler

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("stored_status", ["ENABLED", "DISABLED"])
def test_handler_success_deactivates_user(
    event: dict,
    table,
    stored_user: dict[str, str],
    stored_status: str,
    now: datetime,
) -> None:
    """有効ユーザーを無効化し、無効済みなら全属性を維持して 204・空本文を返す。"""
    # Act
    response = handler.handler(event, None)

    # Assert
    assert response["statusCode"] == 204
    assert response.get("body") in (None, "")
    expected = {**stored_user, "status": "DISABLED"}
    if stored_status == "ENABLED":
        expected["updated_at"] = now.isoformat()
    assert (
        table.get_item(Key={"user_id": stored_user["user_id"]}, ConsistentRead=True)[
            "Item"
        ]
        == expected
    )
