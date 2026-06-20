"""Certificate tamper detection tests — run in CI with PostgreSQL."""

import pytest

pytestmark = pytest.mark.skip(reason="Integration tests require PostgreSQL + Redis")
