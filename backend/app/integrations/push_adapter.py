"""Push subscription storage and Web Push delivery."""

from __future__ import annotations

import json
import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging_config import get_logger
from app.models.analytics_notifications import PushSubscription

logger = get_logger(__name__)


async def upsert_subscription(
    db: AsyncSession,
    *,
    user_id: UUID,
    endpoint: str,
    p256dh: str,
    auth: str,
) -> PushSubscription:
    result = await db.execute(select(PushSubscription).where(PushSubscription.endpoint == endpoint))
    sub = result.scalar_one_or_none()
    if sub:
        sub.user_id = user_id
        sub.p256dh = p256dh
        sub.auth = auth
    else:
        sub = PushSubscription(
            id=uuid.uuid4(),
            user_id=user_id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
        )
        db.add(sub)
    await db.flush()
    return sub


async def send_push_to_user(
    db: AsyncSession,
    *,
    user_id: UUID,
    title: str,
    body: str,
) -> int:
    if not settings.VAPID_PRIVATE_KEY:
        logger.info("push_skipped user_id=%s reason=no_vapid", user_id)
        return 0

    result = await db.execute(select(PushSubscription).where(PushSubscription.user_id == user_id))
    subs = list(result.scalars().all())
    sent = 0
    for sub in subs:
        if await _send_web_push(sub, title, body):
            sent += 1
    return sent


async def _send_web_push(sub: PushSubscription, title: str, body: str) -> bool:
    try:
        from pywebpush import webpush, WebPushException

        payload = json.dumps({"title": title, "body": body})
        webpush(
            subscription_info={
                "endpoint": sub.endpoint,
                "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
            },
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_SUBJECT},
        )
        return True
    except Exception as exc:
        logger.warning("push_failed endpoint=%s error=%s", sub.endpoint[:40], exc)
        return False
