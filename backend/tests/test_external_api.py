"""External API key authentication tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services import api_key_service


@pytest.mark.integration
async def test_external_aggregate_stats_requires_api_key(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/external/aggregate-stats")
    assert res.status_code == 401


@pytest.mark.integration
async def test_external_aggregate_stats_with_valid_key(db_session):
    raw_key, _ = await api_key_service.create_api_key(
        db_session, scopes=["aggregate_stats.read"], label_prefix="test"
    )
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(
            "/api/v1/external/aggregate-stats",
            headers={"X-Api-Key": raw_key},
        )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert "total_centers" in body["data"]
