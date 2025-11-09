import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings


def create_access_token(data: dict) -> str:
    """Generate a short-lived JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.security.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)


def create_refresh_token(data: dict) -> str:
    """Generate a long-lived JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.security.refresh_token_expire_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    return jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
