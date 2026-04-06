from fastapi import Header, HTTPException, status

from app.services.auth import auth_service
from app.services.state import UserRecord


def get_current_user(authorization: str | None = Header(default=None)) -> UserRecord:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    token = authorization.removeprefix("Bearer ").strip()
    user = auth_service.get_user_by_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
        )
    return user

