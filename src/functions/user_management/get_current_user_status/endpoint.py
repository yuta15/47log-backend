"""HTTP endpoint for retrieving the authenticated user's registration status."""

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

from ....modules.user_management.domain import UserIdVo
from ...auth.claims import get_auth_claims
from ...responses import error_response
from ..router import router
from .dependencies import _get_usecase
from .models import GetCurrentUserStatusResponse

logger = Logger(service="47log-backend")


@router.get("/users/me/status")
def get_current_user_status() -> Response:
    """Return the current-user status with the API's HTTP response contract."""
    try:
        claims = get_auth_claims(router.current_event)
        output = _get_usecase().execute(UserIdVo(claims.sub))
        response = GetCurrentUserStatusResponse.model_validate(output)
        return Response(
            status_code=200,
            content_type="application/json",
            body=response.model_dump_json(),
        )
    except UnauthorizedError:
        return error_response(401, "Unauthorized")
    except Exception:
        logger.exception("Current user status request failed")
        return error_response(500, "Internal server error")
