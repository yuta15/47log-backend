"""Load user-management endpoints and expose their shared Router."""

from .get_current_user import (
    endpoint as _get_current_user_endpoint,  # noqa: F401 -- register routes
)
from .router import router

__all__ = ["router"]
