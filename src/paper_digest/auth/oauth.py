# src/paper_digest/auth/oauth.py
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.requests import Request
from starlette.responses import RedirectResponse
import json
from datetime import datetime, timedelta
from jose import JWTError, jwt
from paper_digest.auth.config import settings
from paper_digest.storage.database import (
    create_or_update_user,
    get_user_by_email,
)


oauth = OAuth()

# Register OAuth apps
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="github",
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT token for user session."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str):
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


async def handle_oauth_callback(request: Request, provider: str):
    """Handle OAuth callback from provider."""
    try:
        token = await oauth.create_client(provider).authorize_access_token(request)
    except OAuthError as error:
        return {"error": str(error)}

    # Get user info from provider
    if provider == "google":
        user_info = token.get("userinfo")
        email = user_info.get("email")
        oauth_id = user_info.get("sub")
    elif provider == "github":
        user_info = await oauth.github.get("user", token=token)
        user_data = user_info.json()
        email = user_data.get("email")
        oauth_id = str(user_data.get("id"))

        # If email is not in user profile, get from emails endpoint
        if not email:
            emails = await oauth.github.get("user/emails", token=token)
            emails_data = emails.json()
            for e in emails_data:
                if e.get("primary"):
                    email = e.get("email")
                    break

    # Create or update user in database
    user = create_or_update_user(
        email=email,
        oauth_provider=provider,
        oauth_id=oauth_id,
    )

    # Create JWT token
    access_token = create_access_token(data={"sub": user.id})

    return {
        "user_id": user.id,
        "email": email,
        "access_token": access_token,
        "token_type": "bearer",
    }


def get_current_user_id(token: str) -> str | None:
    """Extract user ID from token."""
    return verify_token(token)
