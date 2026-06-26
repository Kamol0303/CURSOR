"""Group E — branches (training centers) management.

Architecture: TrainingCenter is the branch entity; center_id is the tenant key.
No separate branch_id table — each filial is an independent training center.
"""

from __future__ import annotations

import pytest

from app.core.permissions import ROLE_PERMISSIONS
from app.core.tenant import can_modify_center


class TestGroupEArchitecture:
    def test_centers_permissions_exist(self):
        assert "centers.create" in ROLE_PERMISSIONS["super_admin"]
        assert "centers.read" in ROLE_PERMISSIONS["hokimiyat_operator"]
        assert "centers.update" in ROLE_PERMISSIONS["center_director"]
        assert "centers.delete" in ROLE_PERMISSIONS["super_admin"]
        assert "centers.delete" not in ROLE_PERMISSIONS["hokimiyat_operator"]


class TestGroupECenterModifyRules:
    def test_director_can_modify_own_center_only(self):
        from types import SimpleNamespace
        from uuid import uuid4

        center_id = uuid4()
        director = SimpleNamespace(role=SimpleNamespace(code="center_director"), center_id=center_id)
        other_id = uuid4()
        assert can_modify_center(director, center_id) is True
        assert can_modify_center(director, other_id) is False

    def test_hokimiyat_cannot_modify_center(self):
        from types import SimpleNamespace
        from uuid import uuid4

        hokimiyat = SimpleNamespace(role=SimpleNamespace(code="hokimiyat_operator"), center_id=None)
        assert can_modify_center(hokimiyat, uuid4()) is False


@pytest.mark.integration
class TestGroupEBranchesApi:
    async def test_hokimiyat_lists_all_centers_director_sees_own(self, api_client, security_fixtures):
        fx = security_fixtures
        hokimiyat_res = await api_client.get(
            "/api/v1/centers",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert hokimiyat_res.status_code == 200
        hokimiyat_ids = {item["id"] for item in hokimiyat_res.json()["data"]}
        assert str(fx["center_a"].id) in hokimiyat_ids
        assert str(fx["center_b"].id) in hokimiyat_ids

        director_res = await api_client.get(
            "/api/v1/centers",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert director_res.status_code == 200
        director_data = director_res.json()["data"]
        assert len(director_data) == 1
        assert director_data[0]["id"] == str(fx["center_a"].id)

    async def test_director_cannot_access_other_center(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            f"/api/v1/centers/{fx['center_b'].id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert response.status_code == 403

    async def test_director_updates_own_center(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.patch(
            f"/api/v1/centers/{fx['center_a'].id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"phone": "+998901111111"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["phone"] == "+998901111111"

    async def test_hokimiyat_cannot_delete_center(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.delete(
            f"/api/v1/centers/{fx['center_a'].id}",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 403

    async def test_super_admin_can_create_center(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            "/api/v1/centers",
            headers={"Authorization": f"Bearer {fx['token_super_admin']}"},
            json={"name": "Group E Branch", "center_type": "private"},
        )
        assert response.status_code == 201
        assert response.json()["data"]["name"] == "Group E Branch"

    async def test_geography_endpoints(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        from app.models.education import Mahalla, Region

        region = Region(name_uz="Group E Tuman", name_ru="Group E Tuman", name_en="Group E District")
        db_session.add(region)
        await db_session.flush()
        mahalla = Mahalla(
            region_id=region.id,
            name_uz="Group E Mahalla",
            name_ru="Group E Mahalla",
            name_en="Group E Mahalla",
        )
        db_session.add(mahalla)
        await db_session.commit()

        regions_res = await api_client.get(
            "/api/v1/regions",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert regions_res.status_code == 200
        assert any(r["name_uz"] == "Group E Tuman" for r in regions_res.json()["data"])

        mahallas_res = await api_client.get(
            f"/api/v1/mahallas?region_id={region.id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert mahallas_res.status_code == 200
        assert mahallas_res.json()["data"][0]["name_uz"] == "Group E Mahalla"

        update_res = await api_client.patch(
            f"/api/v1/centers/{fx['center_a'].id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"mahalla_id": str(mahalla.id)},
        )
        assert update_res.status_code == 200
        assert update_res.json()["data"]["mahalla_id"] == str(mahalla.id)
        assert update_res.json()["data"]["mahalla_name_uz"] == "Group E Mahalla"
