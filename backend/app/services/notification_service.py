"""Notification templates and delivery orchestration."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.email_adapter import send_email
from app.integrations.sms_adapter import mask_phone, send_sms
from app.models.analytics_notifications import (
    Notification,
    NotificationLog,
    NotificationPreference,
    SmsLog,
)
from app.models.identity import User

EVENT_TEMPLATES: dict[str, dict[str, tuple[str, str, str, str, str, str]]] = {
    "enrollment": {
        "titles": (
            "Yangi ro'yxatdan o'tish",
            "Новая регистрация",
            "New enrollment",
        ),
        "bodies": (
            "{student_name} {center_name} markaziga ro'yxatdan o'tdi.",
            "{student_name} зарегистрирован в центре {center_name}.",
            "{student_name} enrolled at {center_name}.",
        ),
    },
    "certificate_ready": {
        "titles": (
            "Sertifikat tayyor",
            "Сертификат готов",
            "Certificate ready",
        ),
        "bodies": (
            "{student_name} uchun sertifikat {certificate_number} tayyor.",
            "Сертификат {certificate_number} для {student_name} готов.",
            "Certificate {certificate_number} for {student_name} is ready.",
        ),
    },
    "license_expiry": {
        "titles": (
            "Litsenziya muddati tugaydi",
            "Истекает лицензия",
            "License expiring",
        ),
        "bodies": (
            "{center_name} litsenziyasi {days} kundan keyin tugaydi.",
            "Лицензия центра {center_name} истекает через {days} дней.",
            "License for {center_name} expires in {days} days.",
        ),
    },
    "rating_change": {
        "titles": (
            "Reyting o'zgardi",
            "Изменение рейтинга",
            "Rating changed",
        ),
        "bodies": (
            "{center_name} reytingi {rank}-o'ringa {direction} ({change}).",
            "Рейтинг {center_name} {direction} на позицию {rank} ({change}).",
            "{center_name} rating moved {direction} to rank {rank} ({change}).",
        ),
    },
    "security_alert": {
        "titles": (
            "Xavfsizlik ogohlantirishi",
            "Предупреждение безопасности",
            "Security alert",
        ),
        "bodies": (
            "{message}",
            "{message}",
            "{message}",
        ),
    },
}


def _format_template(template: str, context: dict) -> str:
    try:
        return template.format(**context)
    except KeyError:
        return template


async def get_or_create_preferences(db: AsyncSession, user_id: UUID) -> NotificationPreference:
    pref = await db.get(NotificationPreference, user_id)
    if pref:
        return pref
    pref = NotificationPreference(user_id=user_id, event_types=list(EVENT_TEMPLATES.keys()))
    db.add(pref)
    await db.flush()
    return pref


async def create_notification(
    db: AsyncSession,
    *,
    user_id: UUID,
    event_type: str,
    context: dict,
    channels: list[str] | None = None,
    locale: str = "uz",
) -> Notification | None:
    pref = await get_or_create_preferences(db, user_id)
    if event_type not in pref.event_types and pref.event_types:
        return None

    template = EVENT_TEMPLATES.get(event_type)
    if not template:
        return None

    titles = template["titles"]
    bodies = template["bodies"]
    title_uz, title_ru, title_en = titles
    body_uz = _format_template(bodies[0], context)
    body_ru = _format_template(bodies[1], context)
    body_en = _format_template(bodies[2], context)

    active_channels = channels or []
    if not active_channels:
        if pref.in_app_enabled:
            active_channels.append("in_app")
        if pref.sms_enabled:
            active_channels.append("sms")
        if pref.email_enabled:
            active_channels.append("email")
        if pref.push_enabled:
            active_channels.append("push")
    if not active_channels:
        active_channels = ["in_app"]

    notification = Notification(
        user_id=user_id,
        channel=active_channels[0],
        event_type=event_type,
        title_uz=title_uz,
        title_ru=title_ru,
        title_en=title_en,
        body_uz=body_uz,
        body_ru=body_ru,
        body_en=body_en,
        payload=context,
        locale=locale or pref.locale,
        status="pending",
    )
    db.add(notification)
    await db.flush()

    user = await db.get(User, user_id)
    for channel in active_channels:
        await _deliver_channel(db, notification, user, channel)

    return notification


async def _deliver_channel(
    db: AsyncSession,
    notification: Notification,
    user: User | None,
    channel: str,
) -> None:
    locale = notification.locale or "uz"
    title = getattr(notification, f"title_{locale}", notification.title_uz)
    body = getattr(notification, f"body_{locale}", notification.body_uz)

    if channel == "in_app":
        notification.status = "sent"
        db.add(
            NotificationLog(
                notification_id=notification.id,
                channel="in_app",
                status="sent",
            )
        )
        return

    if channel == "sms" and user and user.phone:
        result = await send_sms(user.phone, f"{title}: {body}")
        db.add(
            SmsLog(
                notification_id=notification.id,
                phone_masked=mask_phone(user.phone),
                provider="eskiz",
                provider_message_id=result.provider_message_id,
                status="sent" if result.success else "failed",
                raw_response=result.raw_response,
            )
        )
        db.add(
            NotificationLog(
                notification_id=notification.id,
                channel="sms",
                status="sent" if result.success else "failed",
                error_message=result.error,
            )
        )
        notification.status = "sent" if result.success else "failed"
        return

    if channel == "email" and user and user.email:
        result = await send_email(user.email, title, body)
        db.add(
            NotificationLog(
                notification_id=notification.id,
                channel="email",
                status="sent" if result.success else "failed",
                error_message=result.error,
            )
        )
        notification.status = "sent" if result.success else "failed"
        return

    if channel == "push" and user:
        from app.integrations.push_adapter import send_push_to_user

        sent_count = await send_push_to_user(db, user_id=user.id, title=title, body=body)
        db.add(
            NotificationLog(
                notification_id=notification.id,
                channel="push",
                status="sent" if sent_count else "skipped",
            )
        )
        notification.status = "sent" if sent_count else "pending"
        return


async def list_notifications(
    db: AsyncSession,
    user_id: UUID,
    *,
    unread_only: bool = False,
    limit: int = 20,
) -> list[Notification]:
    query = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.read_at.is_(None))
    query = query.order_by(Notification.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def mark_read(db: AsyncSession, user_id: UUID, notification_id: UUID) -> bool:
    result = await db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
        .values(read_at=datetime.now(UTC), status="read")
    )
    return result.rowcount > 0


async def mark_all_read(db: AsyncSession, user_id: UUID) -> int:
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        .values(read_at=datetime.now(UTC), status="read")
    )
    return result.rowcount or 0


async def unread_count(db: AsyncSession, user_id: UUID) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user_id, Notification.read_at.is_(None))
    )
    return result.scalar() or 0
