from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from shallowfind.config.settings import settings
from shallowfind.core.security import security, verify_token
from shallowfind.config.database import get_db
from shallowfind.models.user import User
from shallowfind.core.security import TokenData


async def get_token_data(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[TokenData]:
    """
    Extract and verify token data from (1) `Authorization: Bearer <token>`
    or (2) the secure cookie.
    """
    raw_token: Optional[str] = None

    if credentials:  # header first
        raw_token = credentials.credentials
    else:  # then cookie
        raw_token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)

    if not raw_token:
        return None

    return verify_token(raw_token)


async def get_current_user_optional(
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, None if guest or not authenticated."""
    if not token_data or token_data.is_guest:
        return None

    user = db.query(User).filter(User.id == token_data.user_id).first()
    return user


async def get_current_user(
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user (raises exception if not authenticated)."""
    if not token_data or token_data.is_guest:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


async def allow_guest_access(
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> tuple[Optional[User], bool]:
    """Allow both authenticated users and guests. Returns (user, is_guest)."""
    if not token_data:
        return None, True

    if token_data.is_guest:
        return None, True

    user = db.query(User).filter(User.id == token_data.user_id).first()
    return user, False
