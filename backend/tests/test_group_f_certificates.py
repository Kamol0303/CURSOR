"""Group F — certificate file upload and download."""

from __future__ import annotations

import io
import uuid

import pytest

from app.core.permissions import ROLE_PERMISSIONS
from app.services import file_service


class TestGroupFPermissions:
    def test_director_can_create_certificates(self):
        assert "certificates.create" in ROLE_PERMISSIONS["center_director"]

    def test_center_admin_can_create_certificates(self):
        assert "certificates.create" in ROLE_PERMISSIONS["center_admin"]

    def test_teacher_cannot_create_certificates(self):
        assert "certificates.create" not in ROLE_PERMISSIONS["teacher"]


class TestGroupFFilePolicy:
    def test_certificate_mimes(self):
        assert "application/pdf" in file_service.CERTIFICATE_MIMES
        assert "image/jpeg" in file_service.CERTIFICATE_MIMES
        assert "image/png" in file_service.CERTIFICATE_MIMES

    def test_certificate_max_bytes(self):
        assert file_service.CERTIFICATE_MAX_BYTES == 10 * 1024 * 1024


@pytest.mark.integration
class TestGroupFCertificateUpload:
    async def test_create_certificate_with_uploaded_file(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        student = fx["student_a"]

        owner_id = str(uuid.uuid4())
        upload_res = await api_client.post(
            "/api/v1/files",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            files={"file": ("cert.pdf", io.BytesIO(b"%PDF-1.4 test"), "application/pdf")},
            data={
                "center_id": str(fx["center_a"].id),
                "owner_type": "certificate",
                "owner_id": owner_id,
            },
        )
        assert upload_res.status_code == 201
        file_id = upload_res.json()["data"]["id"]

        create_res = await api_client.post(
            "/api/v1/certificates",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "student_id": str(student.id),
                "title": "English Level B1",
                "issue_date": "2026-06-01",
                "file_id": file_id,
            },
        )
        assert create_res.status_code == 201
        data = create_res.json()["data"]
        assert data["file_id"] == file_id
        assert data["student_name"] == student.full_name

        download_res = await api_client.get(
            f"/api/v1/files/{file_id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert download_res.status_code == 200
        assert download_res.content.startswith(b"%PDF")

    async def test_teacher_cannot_create_certificate(self, api_client, security_fixtures):
        fx = security_fixtures
        create_res = await api_client.post(
            "/api/v1/certificates",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
            json={
                "student_id": str(fx["student_a"].id),
                "title": "Blocked",
                "issue_date": "2026-06-01",
                "file_id": str(uuid.uuid4()),
            },
        )
        assert create_res.status_code == 403
