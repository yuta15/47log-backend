"""HTTP endpoint for registering the authenticated user."""

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError
from pydantic import ValidationError

from ....modules.user_management.application import UserAlreadyExistsError
from ....modules.user_management.domain import UserIdVo
from ....modules.user_management.domain.entities.value_objects import AccountNameVo
from ...auth.claims import get_auth_claims
from ...responses import error_response
from ..router import router
from .dependencies import _get_usecase
from .models import CreateUserRequest

logger = Logger(service="47log-backend")


@router.post("/users")
def create_user() -> Response:
    """Register the current user with the API's HTTP response contract."""
    try:
        claims = get_auth_claims(router.current_event)
        body = router.current_event.body
        if body is None:
            return error_response(400, "Bad request")
        request = CreateUserRequest.model_validate_json(body)

        _get_usecase().execute(
            UserIdVo(claims.sub), AccountNameVo(request.account_name)
        )
        return Response(status_code=201, content_type="application/json", body="")
    except UnauthorizedError:
        return error_response(401, "Unauthorized")
    except ValidationError:
        return error_response(400, "Bad request")
    except UserAlreadyExistsError:
        return error_response(409, "Conflict")
    except Exception:
        logger.exception("User registration request failed")
        return error_response(500, "Internal server error")
