from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.services import file_service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("", response_model=ApiResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    center_id: UUID = Form(...),
    owner_type: str = Form(...),
    owner_id: UUID = Form(...),
    user: User = Depends(requires_permission("files.upload")),
    db: AsyncSession = Depends(get_db),
):
    stored = await file_service.save_upload(
        db,
        user,
        file=file,
        center_id=center_id,
        owner_type=owner_type,
        owner_id=owner_id,
    )
    await db.commit()
    return ApiResponse(
        success=True,
        data={
            "id": str(stored.id),
            "file_name": stored.file_name,
            "mime_type": stored.mime_type,
            "size_bytes": stored.size_bytes,
        },
    )


@router.get("/{file_id}", response_model=None)
async def download_file(
    file_id: UUID,
    user: User = Depends(requires_permission("files.read")),
    db: AsyncSession = Depends(get_db),
):
    stored = await file_service.get_file(db, user, file_id)
    path = file_service.resolve_file_path(stored)
    if not path.is_file():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "FILE_MISSING"})
    return FileResponse(path, media_type=stored.mime_type, filename=stored.file_name)
