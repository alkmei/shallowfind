from urllib.parse import urlencode
import httpx
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from shallowfind.config.settings import settings
from shallowfind.config.database import get_db
from .service import AuthService
from shallowfind.schemas.auth import GuestLoginResponse

router = APIRouter()


@router.get("/google/login")
async def google_login():
    params = {
        "response_type": "code",
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    query_string = urlencode(params)
    google_auth_url = f"https://accounts.google.com/o/oauth2/auth?{query_string}"

    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(code: str | None = None, db: Session = Depends(get_db)):
    """Handles the OAuth callback and exchanges code for tokens"""

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    try:
        # Exchange authorization code for access token
        token_data = await exchange_code_for_token(code)

        if not token_data or "access_token" not in token_data:
            raise HTTPException(
                status_code=400, detail="Failed to exchange code for access token"
            )

        # Use your existing AuthService to handle Google login
        auth_service = AuthService(db)
        login_response = await auth_service.google_login(token_data["access_token"])

        response = RedirectResponse(url=f"{settings.FRONTEND_URL}/")
        response.set_cookie(
            key=settings.ACCESS_TOKEN_COOKIE_NAME,
            value=login_response.access_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            httponly=True,
            secure=settings.ENVIRONMENT == "production",  # HTTPS only in production
            samesite="lax",
            path="/",
        )

        # Redirect to frontend success page
        return response

    except Exception:
        # Redirect to frontend error page with error message
        error_url = f"{settings.FRONTEND_URL}/auth/error?message=Authentication failed"
        return RedirectResponse(url=error_url)


@router.post("/guest/login")
async def create_guest_session(
    response: Response, db: Session = Depends(get_db)
) -> GuestLoginResponse:
    """Create a guest session and set JWT cookie"""

    try:
        # Create guest session using existing AuthService
        auth_service = AuthService(db)
        guest_response = auth_service.create_guest_session()

        # Set JWT as secure HTTP-only cookie
        response.set_cookie(
            key=settings.ACCESS_TOKEN_COOKIE_NAME,
            value=guest_response.access_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            httponly=True,
            secure=settings.ENVIRONMENT == "production",  # HTTPS only in production
            samesite="lax",
        )

        return GuestLoginResponse(
            access_token=guest_response.access_token,
            token_type="bearer",
            user=None,
            is_guest=True,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create guest session: {str(e)}"
        )


async def exchange_code_for_token(code: str) -> dict[str, str]:
    """Exchange authorization code for Google access token"""

    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=400, detail=f"Token exchange failed: {response.text}"
            )
