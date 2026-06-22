from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.schemas.groups import EnrollmentCreate, GroupCreate, GroupUpdate
from app.schemas.payments import PaymentCreate, PaymentUpdate
from app.services import group_service, payment_service

groups_router = APIRouter(prefix="/groups", tags=["groups"])


@groups_router.get("", response_model=ApiResponse)
async def list_groups(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    center_id: UUID | None = None,
    user: User = Depends(requires_permission("groups.read")),
    db: AsyncSession = Depends(get_db),
):
    groups, total = await group_service.list_groups(db, user, page=page, per_page=per_page, center_id=center_id)
    return ApiResponse(success=True, data=[g.model_dump() for g in groups], meta={"page": page, "per_page": per_page, "total": total})


@groups_router.post("", response_model=ApiResponse, status_code=201)
async def create_group(
    body: GroupCreate,
    user: User = Depends(requires_permission("groups.create")),
    db: AsyncSession = Depends(get_db),
):
    group = await group_service.create_group(db, user, body)
    enroll_count = 0
    return ApiResponse(success=True, data=group_service.group_to_response(group, enrollment_count=enroll_count).model_dump())


@groups_router.patch("/{group_id}", response_model=ApiResponse)
async def update_group(
    group_id: UUID,
    body: GroupUpdate,
    user: User = Depends(requires_permission("groups.update")),
    db: AsyncSession = Depends(get_db),
):
    group = await group_service.update_group(db, user, group_id, body)
    return ApiResponse(success=True, data=group_service.group_to_response(group).model_dump())


@groups_router.delete("/{group_id}", response_model=ApiResponse)
async def delete_group(
    group_id: UUID,
    user: User = Depends(requires_permission("groups.delete")),
    db: AsyncSession = Depends(get_db),
):
    await group_service.delete_group(db, user, group_id)
    return ApiResponse(success=True, data={"deleted": True})


@groups_router.post("/{group_id}/enroll", response_model=ApiResponse)
async def enroll_student(
    group_id: UUID,
    body: EnrollmentCreate,
    user: User = Depends(requires_permission("groups.enroll")),
    db: AsyncSession = Depends(get_db),
):
    enrollment = await group_service.enroll_student(db, user, group_id, body.student_id)
    return ApiResponse(success=True, data={"enrollment_id": str(enrollment.id)})


subjects_router = APIRouter(prefix="/subjects", tags=["subjects"])


@subjects_router.get("", response_model=ApiResponse)
async def list_subjects(
    user: User = Depends(requires_permission("groups.read")),
    db: AsyncSession = Depends(get_db),
):
    subjects = await group_service.list_subjects(db)
    return ApiResponse(
        success=True,
        data=[
            {"id": str(s.id), "name_uz": s.name_uz, "name_ru": s.name_ru, "name_en": s.name_en}
            for s in subjects
        ],
    )


payments_router = APIRouter(prefix="/payments", tags=["payments"])


@payments_router.get("", response_model=ApiResponse)
async def list_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    user: User = Depends(requires_permission("payments.read")),
    db: AsyncSession = Depends(get_db),
):
    payments, total = await payment_service.list_payments(db, user, page=page, per_page=per_page, status=status)
    return ApiResponse(success=True, data=[p.model_dump() for p in payments], meta={"page": page, "per_page": per_page, "total": total})


@payments_router.post("", response_model=ApiResponse, status_code=201)
async def create_payment(
    body: PaymentCreate,
    user: User = Depends(requires_permission("payments.create")),
    db: AsyncSession = Depends(get_db),
):
    payment = await payment_service.create_payment(db, user, body)
    return ApiResponse(success=True, data=payment_service.payment_to_response(payment).model_dump())


@payments_router.patch("/{payment_id}", response_model=ApiResponse)
async def update_payment(
    payment_id: UUID,
    body: PaymentUpdate,
    user: User = Depends(requires_permission("payments.update")),
    db: AsyncSession = Depends(get_db),
):
    payment = await payment_service.update_payment(db, user, payment_id, body)
    return ApiResponse(success=True, data=payment_service.payment_to_response(payment).model_dump())
