"""Lambda entrypoint for API Gateway HTTP API payload v2 requests."""

from typing import Any

from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

from .user_management import router as user_management_router

app = APIGatewayHttpResolver()
app.include_router(user_management_router)


def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Dispatch each HTTP request to its registered endpoint."""
    return app.resolve(event, context)
