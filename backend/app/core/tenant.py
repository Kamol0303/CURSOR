from uuid import UUID

from fastapi import HTTPException

from app.models.identity import User

DISTRICT_WIDE_ROLES = {"super_admin", "hokimiyat_operator", "auditor"}
CENTER_SCOPED_ROLES = {"center_director", "center_admin", "teacher"}


def assert_center_access(user: User, center_id: UUID) -> None:
    if user.role.code in DISTRICT_WIDE_ROLES:
        return
    if user.center_id != center_id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})


def get_user_center_filter(user: User) -> UUID | None:
    """Returns center_id filter for scoped roles, None for district-wide access."""
    if user.role.code in DISTRICT_WIDE_ROLES:
        return None
    if user.center_id is None:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    return user.center_id


def can_modify_center(user: User, center_id: UUID) -> bool:
    if user.role.code == "super_admin":
        return True
    if user.role.code == "center_director" and user.center_id == center_id:
        return True
    return False
