"""Current-user handler for API Gateway HTTP API JWT-authorized requests."""

import json
import logging
import os
from collections.abc import Mapping
from functools import cache

from pydantic import ValidationError

from ..modules.shared.infra.dynamodb import DynamoDBContext, DynamoDBSettings
from ..modules.shared.infra.utc_clock import UtcClock
from ..modules.user_management.application import (
    GetCurrentUserUsecase,
    UserForbiddenError,
    UserNotFoundError,
)
from ..modules.user_management.domain import UserIdVo
from ..modules.user_management.infra.dynamodb_user_repository import (
    DynamoDBUserRepository,
)
from .models import AuthClaims, GetCurrentUserResponse

logger = logging.getLogger(__name__)


@cache
def _get_usecase() -> GetCurrentUserUsecase:
    """Reuse dependencies across invocations in one execution environment."""
    repository = DynamoDBUserRepository(
        DynamoDBContext(DynamoDBSettings()),
        table_name=os.environ.get("USERS_TABLE_NAME", "users_table"),
        clock=UtcClock(),
    )
    return GetCurrentUserUsecase(repository)


def _parse_auth_claims(event: Mapping[str, object]) -> AuthClaims:
    """Read claims supplied by the trusted JWT authorizer."""
    claims: object = event
    for key in ("requestContext", "authorizer", "jwt", "claims"):
        claims = claims.get(key) if isinstance(claims, Mapping) else None
    return AuthClaims.model_validate(claims)


def _response(status_code: int, body: str) -> dict[str, object]:
    """Return a JSON response in API Gateway proxy format."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": body,
        "isBase64Encoded": False,
    }


def _error_response(status_code: int, message: str) -> dict[str, object]:
    """Return a public error message without internal exception details."""
    return _response(status_code, json.dumps({"message": message}))


def handler(event: Mapping[str, object], context: object) -> dict[str, object]:
    """Validate authentication context and return the registered user's details."""
    try:
        claims = _parse_auth_claims(event)
    except ValidationError:
        return _error_response(401, "Unauthorized")

    try:
        output = _get_usecase().execute(UserIdVo(claims.sub))
        response = GetCurrentUserResponse.model_validate(output)
        return _response(200, response.model_dump_json())
    except UserNotFoundError:
        return _error_response(404, "User not found")
    except UserForbiddenError:
        return _error_response(403, "Forbidden")
    except Exception:
        logger.exception("Current user request failed")
        return _error_response(500, "Internal server error")
