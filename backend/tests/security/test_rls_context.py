"""RLS session variable isolation tests."""

import pytest
from sqlalchemy import text

from app.core.rls import apply_rls_context, clear_rls_context, set_rls_user
from app.core.tenant import TenantContext, clear_tenant_context, set_tenant_context


@pytest.mark.integration
async def test_rls_context_sets_teacher_id(db_session, security_fixtures):
    fx = security_fixtures
    clear_rls_context()
    set_rls_user(fx["teacher_a"])
    await apply_rls_context(db_session)

    role = (await db_session.execute(text("SELECT current_setting('app.role', true)"))).scalar()
    teacher_id = (await db_session.execute(text("SELECT current_setting('app.teacher_id', true)"))).scalar()
    center_id = (await db_session.execute(text("SELECT current_setting('app.center_id', true)"))).scalar()

    assert role == "teacher"
    assert teacher_id == str(fx["teacher_record_a"].id)
    assert center_id == str(fx["center_a"].id)

    clear_rls_context()
    set_rls_user(fx["auditor"])
    await apply_rls_context(db_session)

    teacher_id_after = (
        await db_session.execute(text("SELECT current_setting('app.teacher_id', true)"))
    ).scalar()
    assert teacher_id_after == ""


@pytest.mark.integration
async def test_tenant_context_on_request_state(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {fx['token_director_a']}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["role"] == "center_director"
    assert data["center_id"] == str(fx["center_a"].id)


def test_tenant_context_contextvar_roundtrip():
    clear_tenant_context()
    ctx = TenantContext(
        user_id=__import__("uuid").uuid4(),
        role="teacher",
        center_id=__import__("uuid").uuid4(),
        teacher_id=__import__("uuid").uuid4(),
    )
    set_tenant_context(ctx)
    from app.core.tenant import get_tenant_context

    assert get_tenant_context() == ctx
    clear_tenant_context()
