"""Response model for the current-user handler."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ...modules.user_management.domain import UserStatus


class GetCurrentUserResponse(BaseModel):
    """Serialize user details returned by the current-user use case."""

    model_config = ConfigDict(from_attributes=True)

    account_name: str
    created_at: datetime
    updated_at: datetime
    status: UserStatus
