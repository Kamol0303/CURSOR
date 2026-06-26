from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant import assert_center_access, get_user_center_filter
from app.models.education import Student
from app.models.identity import User
from app.models.operations import StudentPayment
from app.schemas.payments import PaymentCreate, PaymentResponse, PaymentUpdate


def payment_to_response(payment: StudentPayment, student_name: str | None = None) -> PaymentResponse:
    return PaymentResponse(
        id=payment.id,
        student_id=payment.student_id,
        center_id=payment.center_id,
        amount=float(payment.amount),
        currency=payment.currency,
        status=payment.status,
        due_date=payment.due_date,
        paid_at=payment.paid_at,
        payment_method=payment.payment_method,
        discount_percent=float(payment.discount_percent or 0),
        student_name=student_name,
    )


async def list_payments(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
) -> tuple[list[PaymentResponse], int]:
    center_filter = get_user_center_filter(user)
    query = select(StudentPayment, Student.full_name).join(Student, Student.id == StudentPayment.student_id)
    if center_filter:
        query = query.where(StudentPayment.center_id == center_filter)
    if status:
        query = query.where(StudentPayment.status == status)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        query.order_by(StudentPayment.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    )
    return [payment_to_response(row[0], student_name=row[1]) for row in result.all()], total


async def create_payment(db: AsyncSession, user: User, data: PaymentCreate) -> StudentPayment:
    assert_center_access(user, data.center_id)
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    student = (
        await db.execute(select(Student).where(Student.id == data.student_id, Student.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if not student or student.center_id != data.center_id:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})

    payment = StudentPayment(
        student_id=data.student_id,
        center_id=data.center_id,
        amount=data.amount,
        currency=data.currency,
        due_date=data.due_date,
        discount_percent=data.discount_percent,
        notes=data.notes,
        created_by=user.id,
    )
    db.add(payment)
    await db.flush()
    return payment


async def update_payment(
    db: AsyncSession, user: User, payment_id: UUID, data: PaymentUpdate
) -> StudentPayment:
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    result = await db.execute(select(StudentPayment).where(StudentPayment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, payment.center_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(payment, key, value)
    if data.status == "paid" and not payment.paid_at:
        payment.paid_at = datetime.now(UTC)
    payment.updated_at = datetime.now(UTC)
    await db.flush()
    return payment
