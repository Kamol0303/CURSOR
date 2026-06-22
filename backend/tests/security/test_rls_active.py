"""Verify PostgreSQL RLS policies are enabled with FORCE."""

import pytest
from sqlalchemy import text


@pytest.mark.integration
async def test_rls_force_enabled(db_session):
    result = await db_session.execute(
        text("""
            SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname IN ('students', 'enrollments', 'certificates', 'guardians')
            ORDER BY c.relname
        """)
    )
    rows = result.mappings().all()
    assert len(rows) == 4, f"Expected 4 tables, got {rows}"
    for row in rows:
        assert row["relrowsecurity"] is True, f"{row['relname']} missing RLS"
        assert row["relforcerowsecurity"] is True, f"{row['relname']} missing FORCE RLS"
