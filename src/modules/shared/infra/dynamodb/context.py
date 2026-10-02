"""DynamoDB context."""

import boto3
from boto3.resources.base import ServiceResource

from .settings import DynamoDBSettings


class DynamoDBContext:
    """Provide DynamoDB settings and a resource for one execution thread."""

    def __init__(self, settings: DynamoDBSettings) -> None:
        """Create a DynamoDB resource from application settings."""
        self._settings = settings
        self._resource: ServiceResource = boto3.resource(
            "dynamodb",
            region_name=self._settings.region_name,
            endpoint_url=self._settings.endpoint_url,
        )

    @property
    def settings(self) -> DynamoDBSettings:
        """Return the settings owned by this context."""
        return self._settings

    @property
    def resource(self) -> ServiceResource:
        """Return the resource owned by this context."""
        return self._resource
