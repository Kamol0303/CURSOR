from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.tenant import assert_center_access, get_user_center_filter
from app.models.education import Teacher
from app.models.files_messages import Message
from app.models.identity import TrainingCenter, User
from app.schemas.messages import (
    MessageCreate,
    MessageMonitorResponse,
    MessageRecipientResponse,
    MessageResponse,
)

_CENTER_STAFF_ROLES = frozenset({"teacher", "center_admin", "center_director", "accountant"})


async def _teacher_display_names(db: AsyncSession, user_ids: list[UUID]) -> dict[UUID, str]:
    if not user_ids:
        return {}
    rows = await db.execute(
        select(Teacher.user_id, Teacher.full_name).where(
            Teacher.user_id.in_(user_ids),
            Teacher.deleted_at.is_(None),
        )
    )
    return {row[0]: row[1] for row in rows.all() if row[0]}


def _display_name(user: User | None, teacher_names: dict[UUID, str]) -> str | None:
    if not user:
        return None
    return teacher_names.get(user.id) or user.username or user.phone or user.email


def _to_response(msg: Message, teacher_names: dict[UUID, str]) -> MessageResponse:
    return MessageResponse(
        id=msg.id,
        center_id=msg.center_id,
        sender_id=msg.sender_id,
        recipient_id=msg.recipient_id,
        title=msg.title,
        body=msg.body,
        is_read=msg.is_read,
        sent_at=msg.sent_at,
        sender_name=_display_name(msg.sender, teacher_names),
        recipient_name=_display_name(msg.recipient, teacher_names),
    )


async def list_messages(
    db: AsyncSession,
    user: User,
    *,
    box: str = "inbox",
    limit: int = 50,
) -> list[MessageResponse]:
    center_filter = get_user_center_filter(user)
    query = (
        select(Message)
        .options(selectinload(Message.sender), selectinload(Message.recipient))
        .where(Message.deleted_at.is_(None))
        .order_by(Message.sent_at.desc())
        .limit(limit)
    )
    if center_filter:
        query = query.where(Message.center_id == center_filter)
    if box == "sent":
        query = query.where(Message.sender_id == user.id)
    else:
        query = query.where(Message.recipient_id == user.id)

    result = await db.execute(query)
    messages = result.scalars().all()
    user_ids = [
        uid
        for m in messages
        for uid in (m.sender_id, m.recipient_id)
        if uid is not None
    ]
    teacher_names = await _teacher_display_names(db, list(set(user_ids)))
    return [_to_response(m, teacher_names) for m in messages]


async def list_recipients(
    db: AsyncSession,
    user: User,
    *,
    search: str | None = None,
    limit: int = 30,
) -> list[MessageRecipientResponse]:
    if not user.center_id:
        raise HTTPException(status_code=422, detail={"code": "CENTER_REQUIRED"})

    stmt = (
        select(User)
        .options(selectinload(User.role))
        .where(
            User.deleted_at.is_(None),
            User.is_active.is_(True),
            User.is_demo_account.is_(False),
            User.center_id == user.center_id,
            User.id != user.id,
            User.role.has(code=list(_CENTER_STAFF_ROLES)),
        )
        .order_by(User.username.nulls_last())
        .limit(limit)
    )

    if search:
        pattern = f"%{search.strip()}%"
        teacher_user_ids = select(Teacher.user_id).where(
            Teacher.full_name.ilike(pattern),
            Teacher.center_id == user.center_id,
            Teacher.deleted_at.is_(None),
            Teacher.user_id.is_not(None),
        )
        stmt = stmt.where(
            or_(
                User.username.ilike(pattern),
                User.phone.ilike(pattern),
                User.email.ilike(pattern),
                User.id.in_(teacher_user_ids),
            )
        )

    users = (await db.execute(stmt)).scalars().all()
    teacher_names = await _teacher_display_names(db, [u.id for u in users])

    return [
        MessageRecipientResponse(
            id=str(u.id),
            display_name=_display_name(u, teacher_names) or str(u.id),
            role=u.role.code,
            username=u.username,
        )
        for u in users
    ]


async def send_message(db: AsyncSession, user: User, body: MessageCreate) -> MessageResponse:
    center_id = user.center_id
    if not center_id:
        raise HTTPException(status_code=422, detail={"code": "CENTER_REQUIRED"})

    if body.recipient_id == user.id:
        raise HTTPException(status_code=422, detail={"code": "SELF_MESSAGE_FORBIDDEN"})

    recipient = await db.get(User, body.recipient_id)
    if not recipient or not recipient.is_active or recipient.deleted_at is not None:
        raise HTTPException(status_code=404, detail={"code": "RECIPIENT_NOT_FOUND"})

    if not recipient.center_id or recipient.center_id != center_id:
        raise HTTPException(status_code=403, detail={"code": "CROSS_CENTER_FORBIDDEN"})

    msg = Message(
        center_id=center_id,
        sender_id=user.id,
        recipient_id=body.recipient_id,
        channel="in_app",
        title=body.title,
        body=body.body,
    )
    db.add(msg)
    await db.flush()
    msg.sender = user
    msg.recipient = recipient
    teacher_names = await _teacher_display_names(db, [user.id, recipient.id])
    return _to_response(msg, teacher_names)


async def monitor_messages(
    db: AsyncSession,
    user: User,
    *,
    center_id: UUID | None = None,
    limit: int = 100,
) -> list[MessageMonitorResponse]:
    if user.role.code != "super_admin":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    stmt = (
        select(Message, TrainingCenter.name)
        .join(TrainingCenter, Message.center_id == TrainingCenter.id)
        .options(selectinload(Message.sender), selectinload(Message.recipient))
        .where(Message.deleted_at.is_(None))
        .order_by(Message.sent_at.desc())
        .limit(limit)
    )
    if center_id:
        stmt = stmt.where(Message.center_id == center_id)

    rows = (await db.execute(stmt)).all()
    user_ids = [uid for msg, _ in rows for uid in (msg.sender_id, msg.recipient_id) if uid is not None]
    teacher_names = await _teacher_display_names(db, list(set(user_ids)))

    return [
        MessageMonitorResponse(
            id=msg.id,
            center_id=msg.center_id,
            center_name=center_name,
            sender_id=msg.sender_id,
            recipient_id=msg.recipient_id,
            sender_name=_display_name(msg.sender, teacher_names),
            recipient_name=_display_name(msg.recipient, teacher_names),
            title=msg.title,
            body=msg.body,
            sent_at=msg.sent_at,
        )
        for msg, center_name in rows
    ]


async def mark_read(db: AsyncSession, user: User, message_id: UUID) -> bool:
    result = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.recipient_id == user.id,
            Message.deleted_at.is_(None),
        )
    )
    msg = result.scalar_one_or_none()
    if not msg:
        return False
    assert_center_access(user, msg.center_id)
    msg.is_read = True
    return True
