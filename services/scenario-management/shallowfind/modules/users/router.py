from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from shallowfind.modules.users.service import UserService
from shallowfind.config.database import get_db
from shallowfind.schemas.user import UserProfileResponse


router = APIRouter()


@router.get("/{user_id}")
async def get_user(user_id: str, db: Session = Depends(get_db)) -> UserProfileResponse:
    """Fetch user by ID"""
    service = UserService(db)
    user = service.get_user_by_id(user_id)

    return UserProfileResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        google_id=user.google_id,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None,
    )


@router.get("/{user_id}/scenarios")
async def get_user_scenarios(user_id: str, db: Session = Depends(get_db)):
    """Fetch scenarios for a user"""
    pass
