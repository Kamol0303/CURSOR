from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.tenant import assert_center_access, get_user_center_filter
from app.models.files_messages import Message
from app.models.identity import User
from app.schemas.messages import MessageCreate, MessageResponse


def _to_response(msg: Message) -> MessageResponse:
    sender_name = msg.sender.username if msg.sender else None
    recipient_name = msg.recipient.username if msg.recipient else None
    return MessageResponse(
        id=msg.id,
        center_id=msg.center_id,
        sender_id=msg.sender_id,
        recipient_id=msg.recipient_id,
        title=msg.title,
        body=msg.body,
        is_read=msg.is_read,
        sent_at=msg.sent_at,
        sender_name=sender_name,
        recipient_name=recipient_name,
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
    return [_to_response(m) for m in result.scalars().all()]


async def send_message(db: AsyncSession, user: User, body: MessageCreate) -> MessageResponse:
    center_id = user.center_id
    if not center_id:
        raise HTTPException(status_code=422, detail={"code": "CENTER_REQUIRED"})

    recipient = await db.get(User, body.recipient_id)
    if not recipient or not recipient.is_active or recipient.deleted_at is not None:
        raise HTTPException(status_code=404, detail={"code": "RECIPIENT_NOT_FOUND"})
    if recipient.center_id != center_id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

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
    return _to_response(msg)


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
