"""Certificate tamper detection tests — run in CI with PostgreSQL."""

from datetime import UTC, datetime

import pytest

from app.core.rls import apply_rls_context, set_rls_role
from app.models.ratings_certs import Certificate
from app.services.certificate_service import compute_integrity_hash, verify_certificate_public


@pytest.mark.integration
async def test_certificate_tamper_detected(db_session, security_fixtures):
    fx = security_fixtures
    set_rls_role("system")
    await apply_rls_context(db_session)

    cert_num = f"TAMOR-TEST-{fx['student_a'].id.hex[:8].upper()}"
    issue_d = datetime.now(UTC).date()
    cert = Certificate(
        certificate_number=cert_num,
        student_id=fx["student_a"].id,
        center_id=fx["center_a"].id,
        course_name_uz="Test",
        course_name_ru="Test",
        course_name_en="Test",
        issue_date=issue_d,
        integrity_hash=compute_integrity_hash(
            certificate_number=cert_num,
            student_name=fx["student_a"].full_name,
            center_name=fx["center_a"].name,
            course_name="Test",
            issue_date=issue_d,
        ),
    )
    db_session.add(cert)
    await db_session.commit()

    set_rls_role("verifier")
    await apply_rls_context(db_session)
    result = await verify_certificate_public(db_session, cert_num, ip_address="10.0.0.1")
    assert result["valid"] is True

    cert.integrity_hash = "0" * 64
    await db_session.commit()

    result2 = await verify_certificate_public(db_session, cert_num, ip_address="10.0.0.2")
    assert result2["valid"] is False
    assert result2["status"] == "tampered"


@pytest.mark.integration
async def test_verify_rate_limit(api_client):
    statuses = []
    for _ in range(12):
        res = await api_client.get("/api/v1/public/verify/TAMOR-NOTFOUND-XXXX")
        statuses.append(res.status_code)
    assert 429 in statuses
