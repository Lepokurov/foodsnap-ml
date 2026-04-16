from fastapi import APIRouter

from app.core.config import get_settings
from app.db.session import check_database_connection


router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> dict[str, str]:
    settings = get_settings()
    database_ok = check_database_connection()
    return {
        "status": "ok" if database_ok else "degraded",
        "storage": settings.storage_backend,
        "queue": settings.queue_backend,
        "persistence": "postgres" if "postgres" in settings.database_url else "sqlite",
        "database": "connected" if database_ok else "unavailable",
    }
