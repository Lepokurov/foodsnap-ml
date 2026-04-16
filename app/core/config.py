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
    storage_backend: str = getenv("STORAGE_BACKEND", "local")
    local_upload_dir: Path = Path(getenv("LOCAL_UPLOAD_DIR", "data/uploads"))
    s3_bucket_name: str = getenv("S3_BUCKET_NAME", "")
    s3_upload_prefix: str = getenv("S3_UPLOAD_PREFIX", "meal-uploads")
    database_url: str = getenv(
        "DATABASE_URL",
        "postgresql+psycopg:///foodsnap_ml",
    )
    queue_backend: str = getenv("QUEUE_BACKEND", "rabbitmq")
    rabbitmq_url: str = getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    rabbitmq_meal_analysis_queue: str = getenv(
        "RABBITMQ_MEAL_ANALYSIS_QUEUE",
        "foodsnap.meal_analysis",
    )
    rabbitmq_food_reference_import_queue: str = getenv(
        "RABBITMQ_FOOD_REFERENCE_IMPORT_QUEUE",
        "foodsnap.food_reference_import",
    )
    usda_fdc_api_key: str = getenv("USDA_FDC_API_KEY", "DEMO_KEY")
    usda_fdc_base_url: str = getenv(
        "USDA_FDC_BASE_URL",
        "https://api.nal.usda.gov/fdc/v1",
    )
    meal_classifier_backend: str = getenv("MEAL_CLASSIFIER_BACKEND", "stub")
    aws_region: str = getenv("AWS_REGION", "us-east-1")


@lru_cache
def get_settings() -> Settings:
    return Settings()
