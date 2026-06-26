import base64
import hashlib
import io
import secrets
from datetime import UTC, date, datetime
from uuid import UUID

import qrcode
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis_client import check_rate_limit
from app.core.tenant import assert_center_access
from app.models.education import Student, Subject
from app.models.identity import User
from app.models.files_messages import StoredFile
from app.models.ratings_certs import Certificate, CertificateVerification
from app.schemas.certificates import CertificateCreate
from app.services import file_service
from app.services.audit_service import write_audit_log


def _canonical_cert_data(
    *,
    certificate_number: str,
    student_name: str,
    center_name: str,
    course_name: str,
    issue_date: date,
) -> str:
    return f"{certificate_number}|{student_name}|{center_name}|{course_name}|{issue_date.isoformat()}"


def compute_integrity_hash(
    *,
    certificate_number: str,
    student_name: str,
    center_name: str,
    course_name: str,
    issue_date: date,
) -> str:
    data = _canonical_cert_data(
        certificate_number=certificate_number,
        student_name=student_name,
        center_name=center_name,
        course_name=course_name,
        issue_date=issue_date,
    )
    return hashlib.sha256(data.encode()).hexdigest()


def generate_certificate_number() -> str:
    year = datetime.now(UTC).year
    suffix = secrets.token_hex(4).upper()
    return f"TAMOR-{year}-{suffix}"


def generate_qr_base64(certificate_number: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(certificate_number)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1B4D3E", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


async def issue_certificate(
    db: AsyncSession,
    user: User,
    *,
    student_id: UUID,
    subject_id: UUID | None,
    idempotency_key: str | None,
    ip_address: str | None,
) -> Certificate:
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    if idempotency_key:
        existing = await db.execute(
            select(Certificate).where(Certificate.idempotency_key == idempotency_key)
        )
        cert = existing.scalar_one_or_none()
        if cert:
            return cert

    result = await db.execute(
        select(Student)
        .options(selectinload(Student.center))
        .where(Student.id == student_id, Student.deleted_at.is_(None))
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, student.center_id)

    course_uz = course_ru = course_en = "Umumiy kurs"
    if subject_id:
        subject = await db.get(Subject, subject_id)
        if subject:
            course_uz, course_ru, course_en = subject.name_uz, subject.name_ru, subject.name_en

    cert_number = generate_certificate_number()
    issue_date = date.today()
    center_name = student.center.name if student.center else ""
    integrity_hash = compute_integrity_hash(
        certificate_number=cert_number,
        student_name=student.full_name,
        center_name=center_name,
        course_name=course_uz,
        issue_date=issue_date,
    )

    cert = Certificate(
        certificate_number=cert_number,
        student_id=student.id,
        center_id=student.center_id,
        subject_id=subject_id,
        course_name_uz=course_uz,
        course_name_ru=course_ru,
        course_name_en=course_en,
        issue_date=issue_date,
        integrity_hash=integrity_hash,
        idempotency_key=idempotency_key,
        locale=user.locale_preference,
    )
    db.add(cert)
    student.graduation_date = student.graduation_date or issue_date
    await db.flush()

    await write_audit_log(
        db,
        user_id=user.id,
        action="certificate.issue",
        resource_type="certificate",
        resource_id=cert.id,
        ip_address=ip_address,
        details={"certificate_number": cert_number},
    )
    return cert


async def create_certificate_with_file(
    db: AsyncSession,
    user: User,
    data: CertificateCreate,
    *,
    ip_address: str | None,
) -> Certificate:
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    result = await db.execute(
        select(Student)
        .options(selectinload(Student.center))
        .where(Student.id == data.student_id, Student.deleted_at.is_(None))
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, student.center_id)

    stored_result = await db.execute(
        select(StoredFile).where(
            StoredFile.id == data.file_id,
            StoredFile.deleted_at.is_(None),
        )
    )
    stored = stored_result.scalar_one_or_none()
    if not stored:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, stored.center_id)
    if stored.owner_type != file_service.CERTIFICATE_OWNER:
        raise HTTPException(status_code=422, detail={"code": "INVALID_FILE"})
    if stored.center_id != student.center_id:
        raise HTTPException(status_code=422, detail={"code": "CENTER_MISMATCH"})
    if stored.mime_type not in file_service.CERTIFICATE_MIMES:
        raise HTTPException(status_code=415, detail={"code": "UNSUPPORTED_MEDIA_TYPE"})

    course_uz = course_ru = course_en = data.title
    if data.subject_id:
        subject = await db.get(Subject, data.subject_id)
        if subject:
            course_uz, course_ru, course_en = subject.name_uz, subject.name_ru, subject.name_en

    cert_number = generate_certificate_number()
    center_name = student.center.name if student.center else ""
    integrity_hash = compute_integrity_hash(
        certificate_number=cert_number,
        student_name=student.full_name,
        center_name=center_name,
        course_name=course_uz,
        issue_date=data.issue_date,
    )

    cert = Certificate(
        certificate_number=cert_number,
        student_id=student.id,
        center_id=student.center_id,
        subject_id=data.subject_id,
        course_name_uz=course_uz,
        course_name_ru=course_ru,
        course_name_en=course_en,
        issue_date=data.issue_date,
        integrity_hash=integrity_hash,
        locale=user.locale_preference,
        file_id=data.file_id,
    )
    db.add(cert)
    await db.flush()
    stored.owner_id = cert.id
    student.graduation_date = student.graduation_date or data.issue_date
    await db.flush()

    await write_audit_log(
        db,
        user_id=user.id,
        action="certificate.create",
        resource_type="certificate",
        resource_id=cert.id,
        ip_address=ip_address,
        details={"certificate_number": cert_number, "file_id": str(data.file_id)},
    )
    return cert


async def verify_certificate_public(
    db: AsyncSession,
    certificate_number: str,
    *,
    ip_address: str | None,
    user_agent: str | None,
    locale: str = "uz",
) -> dict:
    rate_key = f"verify:ip:{ip_address or 'unknown'}"
    if not await check_rate_limit(rate_key, 10, 60):
        raise HTTPException(status_code=429, detail={"code": "RATE_LIMIT_EXCEEDED"})

    result = await db.execute(
        select(Certificate)
        .options(
            selectinload(Certificate.student),
            selectinload(Certificate.center),
        )
        .where(Certificate.certificate_number == certificate_number, Certificate.deleted_at.is_(None))
    )
    cert = result.scalar_one_or_none()

    if not cert:
        raise HTTPException(status_code=404, detail={"code": "CERTIFICATE_NOT_FOUND"})

    if cert.status == "revoked":
        db.add(
            CertificateVerification(
                certificate_id=cert.id,
                ip_address=ip_address,
                user_agent=user_agent,
                result="revoked",
            )
        )
        course_key = f"course_name_{locale}" if locale in {"uz", "ru", "en"} else "course_name_uz"
        return {
            "valid": False,
            "status": "revoked",
            "holder_name": cert.student.full_name,
            "course_name": getattr(cert, course_key, cert.course_name_uz),
            "center_name": cert.center.name if cert.center else "",
            "issue_date": cert.issue_date.isoformat(),
        }

    center_name = cert.center.name if cert.center else ""
    recomputed = compute_integrity_hash(
        certificate_number=cert.certificate_number,
        student_name=cert.student.full_name,
        center_name=center_name,
        course_name=cert.course_name_uz,
        issue_date=cert.issue_date,
    )
    valid = recomputed == cert.integrity_hash

    db.add(
        CertificateVerification(
            certificate_id=cert.id,
            ip_address=ip_address,
            user_agent=user_agent,
            result="valid" if valid else "tampered",
        )
    )

    course_key = f"course_name_{locale}" if locale in {"uz", "ru", "en"} else "course_name_uz"
    return {
        "valid": valid,
        "status": "valid" if valid else "tampered",
        "holder_name": cert.student.full_name,
        "course_name": getattr(cert, course_key, cert.course_name_uz),
        "center_name": center_name,
        "issue_date": cert.issue_date.isoformat(),
        "certificate_number": cert.certificate_number,
    }


async def list_certificates(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Certificate], int]:
    from sqlalchemy import func

    from app.core.tenant import get_user_center_filter

    center_filter = get_user_center_filter(user)
    query = (
        select(Certificate)
        .options(selectinload(Certificate.student), selectinload(Certificate.center))
        .where(Certificate.deleted_at.is_(None))
    )
    if center_filter:
        query = query.where(Certificate.center_id == center_filter)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    result = await db.execute(
        query.order_by(Certificate.issue_date.desc()).offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total
