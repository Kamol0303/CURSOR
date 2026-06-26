import secrets
import string
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.core.tenant import assert_center_access, can_modify_center, get_user_center_filter
from app.models.identity import Role, TrainingCenter, User
from app.schemas.centers import CenterCreate, CenterOnboardCreate, CenterProfileComplete, CenterUpdate
from app.services.audit_service import write_audit_log

PROFILE_REQUIRED_FIELDS = ("stir", "phone", "address", "director_name", "center_type")

CENTER_CREATE_ROLES = frozenset({"super_admin", "hokimiyat_operator"})


def center_to_response(center: TrainingCenter) -> dict:
    mahalla_name_uz = center.mahalla.name_uz if getattr(center, "mahalla", None) else None
    return {
        "id": str(center.id),
        "name": center.name,
        "stir": center.stir,
        "director_name": center.director_name,
        "phone": center.phone,
        "email": center.email,
        "address": center.address,
        "license_number": center.license_number,
        "license_expiry": center.license_expiry.isoformat() if center.license_expiry else None,
        "center_type": center.center_type,
        "is_active": center.is_active,
        "mahalla_id": str(center.mahalla_id) if center.mahalla_id else None,
        "mahalla_name_uz": mahalla_name_uz,
        "profile_completed": center.profile_completed,
    }


async def _validate_mahalla_id(db: AsyncSession, mahalla_id: UUID | None) -> None:
    if mahalla_id is None:
        return
    from app.services import geography_service

    await geography_service.get_mahalla(db, mahalla_id)


def _generate_temporary_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def missing_profile_fields(center: TrainingCenter) -> list[str]:
    missing: list[str] = []
    if not center.stir:
        missing.append("stir")
    if not center.phone:
        missing.append("phone")
    if not center.address:
        missing.append("address")
    if not center.director_name:
        missing.append("director_name")
    if not center.center_type:
        missing.append("center_type")
    return missing


async def list_centers(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[TrainingCenter], int]:
    center_filter = get_user_center_filter(user)
    query = select(TrainingCenter).where(TrainingCenter.deleted_at.is_(None))
    if center_filter:
        query = query.where(TrainingCenter.id == center_filter)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    result = await db.execute(
        query.options(selectinload(TrainingCenter.mahalla))
        .order_by(TrainingCenter.name)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


async def get_center(db: AsyncSession, user: User, center_id: UUID) -> TrainingCenter:
    result = await db.execute(
        select(TrainingCenter)
        .options(selectinload(TrainingCenter.mahalla))
        .where(TrainingCenter.id == center_id, TrainingCenter.deleted_at.is_(None))
    )
    center = result.scalar_one_or_none()
    if not center:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, center.id)
    return center


async def get_own_center(db: AsyncSession, user: User) -> TrainingCenter:
    if not user.center_id:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    return await get_center(db, user, user.center_id)


async def create_center(db: AsyncSession, user: User, data: CenterCreate) -> TrainingCenter:
    if user.role.code not in CENTER_CREATE_ROLES:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    await _validate_mahalla_id(db, data.mahalla_id)
    center = TrainingCenter(**data.model_dump(), profile_completed=False)
    db.add(center)
    await db.flush()
    return center


async def onboard_center(
    db: AsyncSession,
    user: User,
    data: CenterOnboardCreate,
    *,
    ip_address: str | None = None,
) -> tuple[TrainingCenter, User, str]:
    if user.role.code not in CENTER_CREATE_ROLES:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    existing = await db.execute(select(User).where(User.username == data.director_username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=422, detail={"code": "USERNAME_TAKEN"})

    role_result = await db.execute(select(Role).where(Role.code == "center_director"))
    director_role = role_result.scalar_one_or_none()
    if not director_role:
        raise HTTPException(status_code=500, detail={"code": "ROLE_NOT_FOUND"})

    temp_password = data.temporary_password or _generate_temporary_password()

    center = TrainingCenter(
        name=data.name,
        director_name=data.director_full_name,
        email=data.director_email,
        phone=data.director_phone,
        profile_completed=False,
        is_active=True,
    )
    db.add(center)
    await db.flush()

    director_user = User(
        username=data.director_username,
        email=data.director_email,
        phone=data.director_phone,
        password_hash=hash_password(temp_password),
        role_id=director_role.id,
        center_id=center.id,
        is_active=True,
        must_change_password=True,
    )
    db.add(director_user)
    await db.flush()

    await write_audit_log(
        db,
        user_id=user.id,
        action="center.onboard",
        resource_type="training_center",
        resource_id=center.id,
        ip_address=ip_address,
        details={
            "center_id": str(center.id),
            "director_username": data.director_username,
            "created_by_role": user.role.code,
        },
    )
    return center, director_user, temp_password


async def get_onboarding_status(db: AsyncSession, user: User) -> dict:
    if user.role.code != "center_director" or not user.center_id:
        return {
            "required": False,
            "profile_completed": True,
            "must_change_password": False,
            "missing_fields": [],
        }

    center = await get_own_center(db, user)
    return {
        "required": True,
        "profile_completed": center.profile_completed,
        "must_change_password": user.must_change_password,
        "missing_fields": missing_profile_fields(center),
        "center_id": str(center.id),
        "center_name": center.name,
    }


async def complete_center_profile(
    db: AsyncSession,
    user: User,
    data: CenterProfileComplete,
) -> TrainingCenter:
    if user.role.code != "center_director":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    center = await get_own_center(db, user)
    center.stir = data.stir
    center.director_name = data.director_name
    center.phone = data.phone
    center.email = data.email
    center.address = data.address
    center.license_number = data.license_number
    center.center_type = data.center_type
    center.profile_completed = True
    await db.flush()
    return center


async def update_center(
    db: AsyncSession, user: User, center_id: UUID, data: CenterUpdate
) -> TrainingCenter:
    center = await get_center(db, user, center_id)
    if not can_modify_center(user, center_id):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    payload = data.model_dump(exclude_unset=True)
    if "mahalla_id" in payload:
        await _validate_mahalla_id(db, payload.get("mahalla_id"))
    for key, value in payload.items():
        setattr(center, key, value)
    if not center.profile_completed and not missing_profile_fields(center):
        center.profile_completed = True
    await db.flush()
    return center


async def delete_center(db: AsyncSession, user: User, center_id: UUID) -> None:
    if user.role.code != "super_admin":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    center = await get_center(db, user, center_id)
    from datetime import UTC, datetime

    center.deleted_at = datetime.now(UTC)
    center.is_active = False
