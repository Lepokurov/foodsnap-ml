from dataclasses import dataclass
from functools import lru_cache
from os import getenv
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = getenv("APP_NAME", "FoodSnap ML")
    api_prefix: str = getenv("API_PREFIX", "/api/v1")
    secret_key: str = getenv("SECRET_KEY", "dev-secret-key")
    access_token_ttl_minutes: int = int(getenv("ACCESS_TOKEN_TTL_MINUTES", "1440"))
    local_upload_dir: Path = Path(getenv("LOCAL_UPLOAD_DIR", "data/uploads"))
    database_url: str = getenv(
        "DATABASE_URL",
        "postgresql+psycopg:///foodsnap_ml",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
