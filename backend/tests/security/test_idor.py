"""Security tests for horizontal/vertical privilege escalation (Section 2A.4, 16.5)."""

import pytest

pytestmark = pytest.mark.skip(reason="Integration tests require PostgreSQL + Redis — run in CI")
