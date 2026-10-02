"""DynamoDB implementation of the user repository."""

from collections.abc import Mapping
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import BotoCoreError, ClientError

from ...shared.infra import UtcClock
from ...shared.infra.dynamodb import DynamoDBContext
from ..application import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserRepository,
    UserRepositoryError,
)
from ..domain import User, UserStatus


class DynamoDBUserRepository(UserRepository):
    """Persist users in DynamoDB."""

    def __init__(
        self,
        context: DynamoDBContext,
        *,
        table_name: str,
        clock: UtcClock,
    ) -> None:
        """Initialize the repository with a DynamoDB context."""
        resource = cast(Any, context.resource)
        self._table: Any = resource.Table(table_name)
        self._clock = clock

    def get_user(self, user_id: UUID) -> User | None:
        """Retrieve a user by ID, or return ``None`` when it does not exist."""
        try:
            response = self._table.get_item(
                Key={"user_id": str(user_id)},
                ConsistentRead=True,
            )
        except (BotoCoreError, ClientError) as error:
            raise UserRepositoryError from error
        item = response.get("Item")
        if item is None:
            return None
        return self._to_user(item)

    def create_user(self, user: User) -> None:
        """Create a user without overwriting an existing user."""
        conditional_check_failed = (
            self._table.meta.client.exceptions.ConditionalCheckFailedException
        )
        try:
            self._table.put_item(
                Item=self._to_item(user),
                ConditionExpression=Attr("user_id").not_exists(),
            )
        except conditional_check_failed as error:
            raise UserAlreadyExistsError from error
        except (BotoCoreError, ClientError) as error:
            raise UserRepositoryError from error

    def disable_user(self, user_id: UUID) -> None:
        """Disable a user and update its timestamp."""
        self._update_status(user_id, UserStatus.DISABLED)

    def enable_user(self, user_id: UUID) -> None:
        """Enable a user and update its timestamp."""
        self._update_status(user_id, UserStatus.ENABLED)

    def _update_status(self, user_id: UUID, status: UserStatus) -> None:
        """Update a user's status without creating a missing user."""
        conditional_check_failed = (
            self._table.meta.client.exceptions.ConditionalCheckFailedException
        )
        try:
            self._table.update_item(
                Key={"user_id": str(user_id)},
                UpdateExpression="SET #status = :status, updated_at = :updated_at",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": status.value,
                    ":updated_at": self._clock.now().isoformat(),
                },
                ConditionExpression=Attr("user_id").exists(),
            )
        except conditional_check_failed as error:
            raise UserNotFoundError from error
        except (BotoCoreError, ClientError) as error:
            raise UserRepositoryError from error

    @staticmethod
    def _to_item(user: User) -> dict[str, str]:
        """Convert a user entity to a DynamoDB item."""
        return {
            "user_id": str(user.user_id),
            "account_name": user.account_name,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "status": user.status.value,
        }

    @staticmethod
    def _to_user(item: Mapping[str, object]) -> User:
        """Convert a DynamoDB item to a user entity."""
        return User(
            user_id=UUID(str(item["user_id"])),
            account_name=str(item["account_name"]),
            created_at=datetime.fromisoformat(str(item["created_at"])),
            updated_at=datetime.fromisoformat(str(item["updated_at"])),
            status=UserStatus(str(item["status"])),
        )
