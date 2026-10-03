"""Read authentication claims supplied by an API Gateway JWT authorizer."""

from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from pydantic import ValidationError

from .models import AuthClaims


def get_auth_claims(event: APIGatewayProxyEventV2) -> AuthClaims:
    """Return validated claims or reject missing and invalid subjects."""
    try:
        return AuthClaims.model_validate(event.request_context.authorizer.jwt_claim)
    except ValidationError as error:
        raise UnauthorizedError("Unauthorized") from error
