
from datetime import datetime, timedelta, timezone

from jose import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from app.core.config import settings


# JWT configuration
ALGORITHM = "HS256"

# Argon2 password hashing
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Securely hash a user's password."""
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Verify a password against its stored hash."""
    try:
        return password_hasher.verify(
            hashed_password,
            plain_password
        )
    except (VerifyMismatchError, VerificationError):
        return False


def create_access_token(
    user_id: int,
    expires_minutes: int | None = None
) -> str:
    """Create a signed JWT access token."""

    duration = (
        expires_minutes
        if expires_minutes is not None
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=duration
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[ALGORITHM]
    )
