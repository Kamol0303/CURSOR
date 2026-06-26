"""PINFL encryption at rest (RT-12)."""

import pytest

from app.core.pinfl import decrypt_pinfl, encrypt_pinfl, mask_pinfl


def test_pinfl_encrypted_not_plaintext():
    plain = "12345678901234"
    encrypted = encrypt_pinfl(plain)
    assert plain not in encrypted
    assert decrypt_pinfl(encrypted) == plain


def test_pinfl_mask_hides_middle():
    masked = mask_pinfl("12345678901234")
    assert "12345678901234" not in masked
    assert masked.endswith("01234")


@pytest.mark.integration
async def test_student_stored_encrypted(db_session, security_fixtures):
    fx = security_fixtures
    student = fx["student_b"]
    assert student.jshshir_encrypted is not None
    assert "12345678901234" not in student.jshshir_encrypted
