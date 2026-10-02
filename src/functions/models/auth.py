"""Shared models for claims supplied by a trusted JWT authorizer."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class AuthClaims(BaseModel):
    """Validate the subject of an already verified JWT, allowing other claims."""

    model_config = ConfigDict(extra="ignore")

    sub: Annotated[
        str,
        StringConstraints(
            strict=True, strip_whitespace=True, min_length=1, max_length=255
        ),
    ]
