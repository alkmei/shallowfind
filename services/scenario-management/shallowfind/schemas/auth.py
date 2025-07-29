from pydantic import BaseModel
from typing import Optional

from .user import UserInfo


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserInfo] = None
    is_guest: bool = False


class GuestLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: None = None
    is_guest: bool = True
