"""User-management infrastructure layer."""

from .dynamodb_user_repository import DynamoDBUserRepository

__all__ = ["DynamoDBUserRepository"]
