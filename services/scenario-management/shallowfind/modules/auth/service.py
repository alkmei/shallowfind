from datetime import datetime, timezone
from sqlalchemy.orm import Session
from shallowfind.models.user import User, UserProfile
from shallowfind.schemas.auth import (
    LoginResponse,
    GuestLoginResponse,
)
from shallowfind.schemas.user import UserInfo, UserProfileInfo
from shallowfind.core.security import (
    create_access_token,
    verify_google_token,
    create_guest_token,
    GoogleUserInfo,
)
import uuid


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def google_login(self, google_token: str) -> LoginResponse:
        """Authenticate user with Google OAuth token."""
        # Verify Google token and get user info
        google_user = await verify_google_token(google_token)

        # Find or create user
        user = self.db.query(User).filter(User.google_id == google_user.id).first()

        if not user:
            user = self.create_user_from_google(google_user)
        else:
            # Update user info
            user.email = google_user.email
            user.name = google_user.name
            user.last_login = datetime.now(timezone.utc)
            self.db.commit()

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "is_guest": False}
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserInfo(
                id=str(user.id),
                email=user.email,
                name=user.name,
                google_id=user.google_id,
            ),
            is_guest=False,
        )

    def create_user_from_google(self, google_user: GoogleUserInfo) -> User:
        """Create new user from Google OAuth info."""
        user = User(
            id=uuid.uuid4(),
            google_id=google_user.id,
            email=google_user.email,
            name=google_user.name,
            last_login=datetime.now(timezone.utc),
        )

        self.db.add(user)
        self.db.flush()  # Get the user ID

        # Create user profile
        profile = UserProfile(user_id=user.id, preferences={})
        self.db.add(profile)

        self.db.commit()
        self.db.refresh(user)

        return user

    def create_guest_session(self) -> GuestLoginResponse:
        """Create guest session token."""
        guest_token = create_guest_token()

        return GuestLoginResponse(
            access_token=guest_token,
            token_type="bearer",
            user=None,
            is_guest=True,
        )

    @staticmethod
    def get_user_profile(user: User) -> UserProfileInfo:
        """Get user profile information."""
        created_at = getattr(user, "created_at", None)
        last_login = getattr(user, "last_login", None)

        return UserProfileInfo(
            id=str(user.id),
            email=user.email,
            name=user.name,
            google_id=user.google_id,
            created_at=created_at.isoformat() if created_at else None,
            last_login=last_login.isoformat() if last_login else None,
        )
