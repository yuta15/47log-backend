"""Load user-management endpoints and expose their shared Router."""

from .activate_user import (
    endpoint as _activate_user_endpoint,  # noqa: F401 -- register routes
)
from .create_user import (
    endpoint as _create_user_endpoint,  # noqa: F401 -- register routes
)
from .get_current_user import (
    endpoint as _get_current_user_endpoint,  # noqa: F401 -- register routes
)
from .get_current_user_status import (
    endpoint as _get_current_user_status_endpoint,  # noqa: F401 -- register routes
)
from .router import router

__all__ = ["router"]
