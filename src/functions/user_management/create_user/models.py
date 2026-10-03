"""Request model for the user registration handler."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ....modules.user_management.domain.entities.value_objects import AccountNameVo


class CreateUserRequest(BaseModel):
    """Validate the account name and reject fields outside the API contract."""

    model_config = ConfigDict(extra="forbid")

    account_name: str = Field(alias="accountName", strict=True)

    @field_validator("account_name")
    @classmethod
    def validate_account_name(cls, value: str) -> str:
        """Apply the domain's account-name constraints without normalization."""
        return AccountNameVo(value).value
