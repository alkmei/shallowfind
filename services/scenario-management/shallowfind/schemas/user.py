from typing import Optional
from pydantic import BaseModel


class UserInfo(BaseModel):
    """User information returned in login response."""

    id: str
    email: str
    name: str
    google_id: str


class UserProfileInfo(BaseModel):
    """Complete user profile information."""

    id: str
    email: Optional[str]
    name: Optional[str]
    google_id: Optional[str]
    created_at: Optional[str]
    last_login: Optional[str]


class UserProfileResponse(BaseModel):
    id: str
    email: Optional[str]
    name: Optional[str]
    google_id: Optional[str]
    created_at: str
    last_login: Optional[str]
