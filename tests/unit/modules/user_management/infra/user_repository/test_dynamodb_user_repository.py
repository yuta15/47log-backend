"""DynamoDBUserRepository のテスト。"""

from datetime import timedelta

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError

from src.modules.user_management.application import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserRepositoryError,
)
from src.modules.user_management.domain import User, UserIdVo
from src.modules.user_management.domain.entities.value_objects import AccountNameVo


def test_get_user_success_returns_mapped_user(
    repository, table, user: User, user_id: UserIdVo
) -> None:
    """DynamoDB item が User エンティティに変換されることを確認する。"""
    # Arrange
    table.get_item.return_value = {
        "Item": {
            "user_id": user.user_id.value,
            "account_name": user.account_name.value,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "status": user.status.value,
        }
    }

    # Act
    actual_user = repository.get_user(user_id)

    # Assert
    assert actual_user is not None
    assert actual_user.user_id == user.user_id
    assert actual_user.account_name == user.account_name
    assert actual_user.created_at == user.created_at
    assert actual_user.updated_at == user.updated_at
    assert actual_user.status is user.status
    table.get_item.assert_called_once_with(
        Key={"user_id": user_id.value},
        ConsistentRead=True,
    )


def test_get_user_success_returns_none_when_item_does_not_exist(
    repository, table, user_id: UserIdVo
) -> None:
    """DynamoDB item がない場合に None を返すことを確認する。"""
    # Arrange
    table.get_item.return_value = {}

    # Act
    actual_user = repository.get_user(user_id)

    # Assert
    assert actual_user is None


def test_get_user_failure_raises_when_dynamodb_returns_an_error(
    repository, table, user_id: UserIdVo
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
        "user_id": user.user_id.value,
        "account_name": user.account_name.value,
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


def test_update_user_success_persists_domain_changes(
    repository, table, user: User, clock
) -> None:
    """ドメインで変更した名前・状態・更新日時をそのまま保存することを確認する。"""
    # Arrange
    user.update_account_name(AccountNameVo("renamed-account"))
    user.disable()
    clock.now.return_value = user.updated_at + timedelta(seconds=1)

    # Act
    repository.update_user(user)

    # Assert
    table.update_item.assert_called_once()
    call_arguments = table.update_item.call_args.kwargs
    assert call_arguments["Key"] == {"user_id": user.user_id.value}
    assert call_arguments["UpdateExpression"] == (
        "SET account_name = :account_name, #status = :status, updated_at = :updated_at"
    )
    assert call_arguments["ExpressionAttributeNames"] == {"#status": "status"}
    assert call_arguments["ExpressionAttributeValues"] == {
        ":account_name": user.account_name.value,
        ":status": user.status.value,
        ":updated_at": user.updated_at.isoformat(),
    }


def test_update_user_failure_raises_when_user_does_not_exist(
    repository, table, user: User, conditional_check_failed_exception
) -> None:
    """条件付き書込み失敗がユーザー未登録例外へ変換されることを確認する。"""
    # Arrange
    table.update_item.side_effect = conditional_check_failed_exception()

    # Assert
    with pytest.raises(UserNotFoundError):
        repository.update_user(user)


@pytest.mark.parametrize(
    "error",
    [
        ClientError(
            {"Error": {"Code": "ProvisionedThroughputExceededException"}},
            "UpdateItem",
        ),
        EndpointConnectionError(endpoint_url="http://localhost:8000"),
    ],
)
def test_update_user_failure_raises_when_dynamodb_returns_an_error(
    repository, table, user: User, error: Exception
) -> None:
    """サービスエラーと接続障害が Repository 例外へ変換されることを確認する。"""
    # Arrange
    table.update_item.side_effect = error

    # Assert
    with pytest.raises(UserRepositoryError):
        repository.update_user(user)
