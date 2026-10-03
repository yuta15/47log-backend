"""Authentication model constraint tests."""

import pytest
from pydantic import ValidationError

from src.functions.auth.models import AuthClaims


@pytest.mark.parametrize("subject", ["a", "a" * 255])
def test_auth_claims_success_accepts_subject_length_boundaries(subject: str) -> None:
    """sub の長さの下限 1 文字と上限 255 文字を許容する。"""
    actual = AuthClaims(sub=subject)

    assert actual.sub == subject


def test_auth_claims_success_strips_subject_whitespace() -> None:
    """sub の前後の空白を除去する。"""
    actual = AuthClaims(sub="  user-1  ")

    assert actual.sub == "user-1"


@pytest.mark.parametrize("subject", [None, 123, "", "  ", "a" * 256])
def test_auth_claims_failure_rejects_invalid_subject(subject: object) -> None:
    """文字列以外・空文字・空白のみ・最大長超過の sub を拒否する。"""
    with pytest.raises(ValidationError):
        AuthClaims.model_validate({"sub": subject})


def test_auth_claims_failure_requires_subject() -> None:
    """sub の欠落を拒否する。"""
    with pytest.raises(ValidationError):
        AuthClaims.model_validate({})
