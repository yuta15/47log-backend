"""HTTP endpoint for deactivating the authenticated user."""

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

from ....modules.user_management.application import UserNotFoundError
from ....modules.user_management.domain import UserIdVo
from ...auth.claims import get_auth_claims
from ...responses import error_response
from ..router import router
from .dependencies import _get_usecase

logger = Logger(service="47log-backend")


@router.post("/users/me/deactivate")
def deactivate_user() -> Response:
    """Deactivate the current user with the API's HTTP response contract."""
    try:
        claims = get_auth_claims(router.current_event)
        _get_usecase().execute(UserIdVo(claims.sub))
        return Response(status_code=204, content_type="application/json", body="")
    except UnauthorizedError:
        return error_response(401, "Unauthorized")
    except UserNotFoundError:
        return error_response(404, "User not found")
    except Exception:
        logger.exception("User deactivation request failed")
        return error_response(500, "Internal server error")
