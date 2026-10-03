"""Response model for the current-user status handler."""

from pydantic import BaseModel, ConfigDict

from ....modules.user_management.application import CurrentUserStatus


class GetCurrentUserStatusResponse(BaseModel):
    """Serialize the authenticated user's registration status."""

    model_config = ConfigDict(from_attributes=True)

    status: CurrentUserStatus
