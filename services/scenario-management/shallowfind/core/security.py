from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import httpx
from ..config.settings import settings

# HTTP Bearer token security
security = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    is_guest: bool = False


class GoogleUserInfo(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    verified_email: bool = False


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str | None = payload.get("sub")
        email: str | None = payload.get("email")
        is_guest: bool = payload.get("is_guest", False)

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        return TokenData(user_id=user_id, email=email, is_guest=is_guest)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def create_guest_token() -> str:
    """Create a guest access token."""
    guest_data: Dict[str, Any] = {"sub": "guest", "email": None, "is_guest": True}
    return create_access_token(guest_data)


async def verify_google_token(token: str) -> GoogleUserInfo:
    """Verify Google OAuth token and get user info."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?access_token={token}"
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token",
                )

            # Get user profile information
            profile_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token}"},
            )

            if profile_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not fetch user profile",
                )

            profile_data = profile_response.json()

            return GoogleUserInfo(
                id=profile_data["id"],
                email=profile_data["email"],
                name=profile_data.get("name", ""),
                picture=profile_data.get("picture"),
                verified_email=profile_data.get("verified_email", False),
            )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not verify Google token",
        )
