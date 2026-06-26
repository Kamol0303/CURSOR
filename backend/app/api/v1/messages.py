from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.schemas.messages import MessageCreate
from app.services import message_service

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("", response_model=ApiResponse)
async def list_messages(
    box: str = Query("inbox", pattern="^(inbox|sent)$"),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(requires_permission("messages.read")),
    db: AsyncSession = Depends(get_db),
):
    items = await message_service.list_messages(db, user, box=box, limit=limit)
    return ApiResponse(success=True, data=[i.model_dump() for i in items])


@router.post("", response_model=ApiResponse, status_code=201)
async def send_message(
    body: MessageCreate,
    user: User = Depends(requires_permission("messages.send")),
    db: AsyncSession = Depends(get_db),
):
    msg = await message_service.send_message(db, user, body)
    await db.commit()
    return ApiResponse(success=True, data=msg.model_dump())


@router.patch("/{message_id}/read", response_model=ApiResponse)
async def mark_message_read(
    message_id: UUID,
    user: User = Depends(requires_permission("messages.read")),
    db: AsyncSession = Depends(get_db),
):
    ok = await message_service.mark_read(db, user, message_id)
    if not ok:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    await db.commit()
    return ApiResponse(success=True, data={"read": True})
