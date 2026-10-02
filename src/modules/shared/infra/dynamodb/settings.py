"""DynamoDB connection settings."""

from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DynamoDBSettings(BaseSettings):
    """Represent settings used to connect to DynamoDB."""

    model_config = SettingsConfigDict(extra="ignore", populate_by_name=True)

    region_name: Annotated[str, Field(validation_alias="AWS_REGION")] = "ap-northeast-1"
    endpoint_url: Annotated[
        str | None, Field(validation_alias="DYNAMODB_ENDPOINT_URL")
    ] = None
