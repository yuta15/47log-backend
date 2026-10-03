"""HTTP endpoint for retrieving the authenticated user."""

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

from ....modules.user_management.application import (
    UserForbiddenError,
    UserNotFoundError,
)
from ....modules.user_management.domain import UserIdVo
from ...auth.claims import get_auth_claims
from ...responses import error_response
from ..router import router
from .dependencies import _get_usecase
from .models import GetCurrentUserResponse

logger = Logger(service="47log-backend")


@router.get("/users/me")
def get_current_user() -> Response:
    """Return current-user details with the API's HTTP response contract."""
    try:
        claims = get_auth_claims(router.current_event)
        output = _get_usecase().execute(UserIdVo(claims.sub))
        response = GetCurrentUserResponse.model_validate(output)
        return Response(
            status_code=200,
            content_type="application/json",
            body=response.model_dump_json(by_alias=True),
        )
    except UnauthorizedError:
        return error_response(401, "Unauthorized")
    except UserNotFoundError:
        return error_response(404, "User not found")
    except UserForbiddenError:
        return error_response(403, "Forbidden")
    except Exception:
        logger.exception("Current user request failed")
        return error_response(500, "Internal server error")
