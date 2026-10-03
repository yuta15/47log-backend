"""Shared HTTP response builders for API endpoints."""

import json

from aws_lambda_powertools.event_handler import Response


def error_response(status_code: int, message: str) -> Response:
    """Return a public JSON error without internal exception details."""
    return Response(
        status_code=status_code,
        content_type="application/json",
        body=json.dumps({"message": message}),
    )
