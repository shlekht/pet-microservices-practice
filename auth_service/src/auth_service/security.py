from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from auth_service.config import settings
from auth_service.models import User

password_hash = PasswordHash.recommended()


def hash_password(password: str):
    return password_hash.hash(password)


def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)


def create_access_token(user: User):
    now = datetime.now(UTC)
    expires_in = now + timedelta(seconds=3600)

    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": "user",
        "exp_in": expires_in,
        "iss": "auth-service"
    }

    token = jwt.encode(
        payload=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return token
