import jwt
from jwt.exceptions import InvalidTokenError

from order_service.config import JWT_PUBLIC_KEY


def decode_access_token(token: str) -> dict:
    
    try:
        payload = jwt.decode(
            token,
            key=JWT_PUBLIC_KEY,
            algorithms=["RS256"],
            issuer="auth-service",
            options={
                "require": ["exp", "sub", "iss"],
            },
        )
        return payload

    except InvalidTokenError as exc:
        raise ValueError("Invalid access token") from exc