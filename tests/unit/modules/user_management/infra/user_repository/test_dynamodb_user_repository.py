"""DynamoDBUserRepository のテスト。"""

from datetime import datetime
from uuid import UUID

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError

from src.modules.user_management.application import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserRepositoryError,
)
from src.modules.user_management.domain import User, UserStatus


def test_get_user_success_returns_mapped_user(
    repository, table, user: User, user_id: UUID
) -> None:
    """DynamoDB item が User エンティティに変換されることを確認する。"""
    # Arrange
    table.get_item.return_value = {
        "Item": {
            "user_id": str(user.user_id),
            "account_name": user.account_name,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "status": user.status.value,
        }
    }

    # Act
    actual_user = repository.get_user(user_id)

    # Assert
    assert actual_user == user


def test_get_user_success_returns_none_when_item_does_not_exist(
    repository, table, user_id: UUID
) -> None:
    """DynamoDB item がない場合に None を返すことを確認する。"""
    # Arrange
    table.get_item.return_value = {}

    # Act
    actual_user = repository.get_user(user_id)

    # Assert
    assert actual_user is None


def test_get_user_failure_raises_when_dynamodb_returns_an_error(
    repository, table, user_id: UUID
) -> None:
    """DynamoDB のサービスエラーが Repository 例外へ変換されることを確認する。"""
    # Arrange
    table.get_item.side_effect = ClientError(
        {"Error": {"Code": "AccessDeniedException", "Message": "Access denied"}},
        "GetItem",
    )

    # Assert
    with pytest.raises(UserRepositoryError):
        repository.get_user(user_id)


def test_create_user_success_writes_a_mapped_item(
    repository, table, user: User
) -> None:
    """User エンティティが DynamoDB 書込み用 item に変換されることを確認する。"""
    # Act
    repository.create_user(user)

    # Assert
    table.put_item.assert_called_once()
    call_arguments = table.put_item.call_args.kwargs
    assert call_arguments["Item"] == {
        "user_id": str(user.user_id),
        "account_name": user.account_name,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "status": user.status.value,
    }


def test_create_user_failure_raises_when_user_already_exists(
    repository, table, user: User, conditional_check_failed_exception
) -> None:
    """条件付き書込み失敗が重複ユーザー例外へ変換されることを確認する。"""
    # Arrange
    table.put_item.side_effect = conditional_check_failed_exception()

    # Assert
    with pytest.raises(UserAlreadyExistsError):
        repository.create_user(user)


def test_create_user_failure_raises_when_dynamodb_endpoint_is_unavailable(
    repository, table, user: User
) -> None:
    """DynamoDB の接続障害が Repository 例外へ変換されることを確認する。"""
    # Arrange
    table.put_item.side_effect = EndpointConnectionError(
        endpoint_url="http://localhost:8000"
    )

    # Assert
    with pytest.raises(UserRepositoryError):
        repository.create_user(user)


def test_disable_user_success_sets_disabled_status_and_updated_at(
    repository, table, updated_at: datetime, user_id: UUID
) -> None:
    """ユーザー無効化で status と更新日時だけが更新されることを確認する。"""
    # Act
    repository.disable_user(user_id)

    # Assert
    call_arguments = table.update_item.call_args.kwargs
    assert call_arguments["ExpressionAttributeValues"] == {
        ":status": UserStatus.DISABLED.value,
        ":updated_at": updated_at.isoformat(),
    }


def test_disable_user_failure_raises_when_user_does_not_exist(
    repository, table, user_id: UUID, conditional_check_failed_exception
) -> None:
    """条件付き書込み失敗がユーザー未登録例外へ変換されることを確認する。"""
    # Arrange
    table.update_item.side_effect = conditional_check_failed_exception()

    # Assert
    with pytest.raises(UserNotFoundError):
        repository.disable_user(user_id)


def test_disable_user_failure_raises_when_dynamodb_returns_an_error(
    repository, table, user_id: UUID
) -> None:
    """DynamoDB のサービスエラーが Repository 例外へ変換されることを確認する。"""
    # Arrange
    table.update_item.side_effect = ClientError(
        {"Error": {"Code": "ProvisionedThroughputExceededException"}},
        "UpdateItem",
    )

    # Assert
    with pytest.raises(UserRepositoryError):
        repository.disable_user(user_id)


def test_enable_user_success_sets_enabled_status_and_updated_at(
    repository, table, updated_at: datetime, user_id: UUID
) -> None:
    """ユーザー有効化で status と更新日時だけが更新されることを確認する。"""
    # Act
    repository.enable_user(user_id)

    # Assert
    call_arguments = table.update_item.call_args.kwargs
    assert call_arguments["ExpressionAttributeValues"] == {
        ":status": UserStatus.ENABLED.value,
        ":updated_at": updated_at.isoformat(),
    }


def test_enable_user_failure_raises_when_user_does_not_exist(
    repository, table, user_id: UUID, conditional_check_failed_exception
) -> None:
    """条件付き書込み失敗がユーザー未登録例外へ変換されることを確認する。"""
    # Arrange
    table.update_item.side_effect = conditional_check_failed_exception()

    # Assert
    with pytest.raises(UserNotFoundError):
        repository.enable_user(user_id)
