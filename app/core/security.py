import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import get_settings


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{base64.b64encode(salt).decode()}:{base64.b64encode(derived).decode()}"


def verify_password(password: str, password_hash: str) -> bool:
    encoded_salt, encoded_hash = password_hash.split(":")
    salt = base64.b64decode(encoded_salt.encode())
    expected = base64.b64decode(encoded_hash.encode())
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return hmac.compare_digest(actual, expected)


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_ttl_minutes
    )
    random_part = secrets.token_urlsafe(24)
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        f"{user_id}:{random_part}:{expires_at.isoformat()}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{user_id}.{int(expires_at.timestamp())}.{random_part}.{signature}"

