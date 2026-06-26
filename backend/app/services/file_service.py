import mimetypes
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.tenant import assert_center_access
from app.models.files_messages import StoredFile
from app.models.identity import User

ALLOWED_MIME_TYPES = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/pdf",
    }
)


def _ensure_upload_dir() -> Path:
    root = Path(settings.FILE_UPLOAD_DIR)
    root.mkdir(parents=True, exist_ok=True)
    return root


STUDENT_PHOTO_MIMES = frozenset({"image/jpeg", "image/png"})
STUDENT_PHOTO_OWNER = "student_photo"
CERTIFICATE_MIMES = frozenset({"application/pdf", "image/jpeg", "image/png"})
CERTIFICATE_OWNER = "certificate"
CERTIFICATE_MAX_BYTES = 10 * 1024 * 1024


async def save_upload(
    db: AsyncSession,
    user: User,
    *,
    file: UploadFile,
    center_id: UUID,
    owner_type: str,
    owner_id: UUID,
) -> StoredFile:
    assert_center_access(user, center_id)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail={"code": "EMPTY_FILE"})
    max_bytes = settings.MAX_UPLOAD_BYTES
    if owner_type == STUDENT_PHOTO_OWNER:
        max_bytes = min(max_bytes, 5 * 1024 * 1024)
    elif owner_type == CERTIFICATE_OWNER:
        max_bytes = CERTIFICATE_MAX_BYTES
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail={"code": "FILE_TOO_LARGE"})

    mime_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
    if owner_type == STUDENT_PHOTO_OWNER:
        allowed = STUDENT_PHOTO_MIMES
    elif owner_type == CERTIFICATE_OWNER:
        allowed = CERTIFICATE_MIMES
    else:
        allowed = ALLOWED_MIME_TYPES
    if mime_type not in allowed:
        raise HTTPException(status_code=415, detail={"code": "UNSUPPORTED_MEDIA_TYPE"})

    file_id = uuid.uuid4()
    ext = Path(file.filename or "upload").suffix.lower()[:10] or ".bin"
    relative_path = f"{center_id}/{file_id}{ext}"
    upload_root = _ensure_upload_dir()
    absolute_path = upload_root / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_bytes(content)

    stored = StoredFile(
        id=file_id,
        center_id=center_id,
        owner_type=owner_type,
        owner_id=owner_id,
        file_name=file.filename or f"{file_id}{ext}",
        mime_type=mime_type,
        storage_path=str(relative_path),
        size_bytes=len(content),
        uploaded_by=user.id,
    )
    db.add(stored)
    await db.flush()
    return stored


async def assert_file_access(db: AsyncSession, user: User, stored: StoredFile) -> None:
    if user.role.code == "super_admin":
        return

    if stored.owner_type == STUDENT_PHOTO_OWNER:
        from app.models.education import Student
        from app.services import parent_service

        student = await db.get(Student, stored.owner_id)
        if not student:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
        if user.role.code == "student" and student.user_id == user.id:
            return
        if user.role.code == "parent":
            children = await parent_service.get_children_for_parent(db, user)
            if student.id in {c.id for c in children}:
                return
        assert_center_access(user, stored.center_id)
        return

    if stored.owner_type == CERTIFICATE_OWNER:
        from app.models.ratings_certs import Certificate
        from app.services import parent_service

        cert = (
            await db.execute(
                select(Certificate).where(
                    Certificate.id == stored.owner_id,
                    Certificate.deleted_at.is_(None),
                )
            )
        ).scalar_one_or_none()
        if not cert:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
        if user.role.code == "student":
            from app.models.education import Student

            student = await db.get(Student, cert.student_id)
            if student and student.user_id == user.id:
                return
        if user.role.code == "parent":
            children = await parent_service.get_children_for_parent(db, user)
            if cert.student_id in {c.id for c in children}:
                return
        assert_center_access(user, cert.center_id)
        return

    assert_center_access(user, stored.center_id)


async def get_file(db: AsyncSession, user: User, file_id: UUID) -> StoredFile:
    result = await db.execute(select(StoredFile).where(StoredFile.id == file_id, StoredFile.deleted_at.is_(None)))
    stored = result.scalar_one_or_none()
    if not stored:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    await assert_file_access(db, user, stored)
    return stored


def resolve_file_path(stored: StoredFile) -> Path:
    return Path(settings.FILE_UPLOAD_DIR) / stored.storage_path
