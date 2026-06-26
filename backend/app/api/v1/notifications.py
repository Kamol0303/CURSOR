from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


class PreferencesUpdate(BaseModel):
    in_app_enabled: bool | None = None
    sms_enabled: bool | None = None
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    locale: str | None = Field(default=None, pattern="^(uz|ru|en)$")
    event_types: list[str] | None = None


class PushSubscribeRequest(BaseModel):
    endpoint: str = Field(min_length=1)
    keys: dict = Field(min_length=1)


@router.get("", response_model=ApiResponse)
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await notification_service.list_notifications(
        db, user.id, unread_only=unread_only, limit=limit
    )
    locale = user.locale_preference or "uz"
    data = [
        {
            "id": str(n.id),
            "event_type": n.event_type,
            "title": getattr(n, f"title_{locale}", n.title_uz),
            "body": getattr(n, f"body_{locale}", n.body_uz),
            "status": n.status,
            "read_at": n.read_at.isoformat() if n.read_at else None,
            "created_at": n.created_at.isoformat(),
            "payload": n.payload,
        }
        for n in items
    ]
    unread = await notification_service.unread_count(db, user.id)
    return ApiResponse(success=True, data=data, meta={"unread_count": unread})


@router.get("/unread-count", response_model=ApiResponse)
async def get_unread_count(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await notification_service.unread_count(db, user.id)
    return ApiResponse(success=True, data={"unread_count": count})


@router.patch("/{notification_id}/read", response_model=ApiResponse)
async def mark_notification_read(
    notification_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await notification_service.mark_read(db, user.id, notification_id)
    if not ok:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    await db.commit()
    return ApiResponse(success=True, data={"read": True})


@router.post("/read-all", response_model=ApiResponse)
async def mark_all_read(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await notification_service.mark_all_read(db, user.id)
    await db.commit()
    return ApiResponse(success=True, data={"marked_read": count})


@router.get("/preferences", response_model=ApiResponse)
async def get_preferences(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pref = await notification_service.get_or_create_preferences(db, user.id)
    return ApiResponse(
        success=True,
        data={
            "in_app_enabled": pref.in_app_enabled,
            "sms_enabled": pref.sms_enabled,
            "email_enabled": pref.email_enabled,
            "push_enabled": pref.push_enabled,
            "locale": pref.locale,
            "event_types": pref.event_types,
        },
    )


@router.patch("/preferences", response_model=ApiResponse)
async def update_preferences(
    body: PreferencesUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pref = await notification_service.get_or_create_preferences(db, user.id)
    if body.in_app_enabled is not None:
        pref.in_app_enabled = body.in_app_enabled
    if body.sms_enabled is not None:
        pref.sms_enabled = body.sms_enabled
    if body.email_enabled is not None:
        pref.email_enabled = body.email_enabled
    if body.push_enabled is not None:
        pref.push_enabled = body.push_enabled
    if body.locale is not None:
        pref.locale = body.locale
    if body.event_types is not None:
        pref.event_types = body.event_types
    await db.commit()
    return ApiResponse(success=True, data={"updated": True})


@router.post("/push-subscribe", response_model=ApiResponse)
async def push_subscribe(
    body: PushSubscribeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.integrations.push_adapter import upsert_subscription

    keys = body.keys or {}
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")
    if not p256dh or not auth:
        raise HTTPException(status_code=422, detail={"code": "INVALID_SUBSCRIPTION"})
    await upsert_subscription(
        db,
        user_id=user.id,
        endpoint=body.endpoint,
        p256dh=p256dh,
        auth=auth,
    )
    pref = await notification_service.get_or_create_preferences(db, user.id)
    pref.push_enabled = True
    await db.commit()
    return ApiResponse(success=True, data={"subscribed": True})
