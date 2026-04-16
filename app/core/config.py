from dataclasses import dataclass, field
from functools import lru_cache
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = field(default_factory=lambda: getenv("APP_NAME", "FoodSnap ML"))
    api_prefix: str = field(default_factory=lambda: getenv("API_PREFIX", "/api/v1"))
    secret_key: str = field(default_factory=lambda: getenv("SECRET_KEY", "dev-secret-key"))
    access_token_ttl_minutes: int = field(
        default_factory=lambda: int(getenv("ACCESS_TOKEN_TTL_MINUTES", "1440"))
    )
    storage_backend: str = field(default_factory=lambda: getenv("STORAGE_BACKEND", "local"))
    local_upload_dir: Path = field(
        default_factory=lambda: Path(getenv("LOCAL_UPLOAD_DIR", "data/uploads"))
    )
    s3_bucket_name: str = field(default_factory=lambda: getenv("S3_BUCKET_NAME", ""))
    s3_upload_prefix: str = field(default_factory=lambda: getenv("S3_UPLOAD_PREFIX", "meal-uploads"))
    database_url: str = field(
        default_factory=lambda: getenv("DATABASE_URL", "postgresql+psycopg:///foodsnap_ml")
    )
    queue_backend: str = field(default_factory=lambda: getenv("QUEUE_BACKEND", "rabbitmq"))
    rabbitmq_url: str = field(
        default_factory=lambda: getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    )
    rabbitmq_meal_analysis_queue: str = field(
        default_factory=lambda: getenv("RABBITMQ_MEAL_ANALYSIS_QUEUE", "foodsnap.meal_analysis")
    )
    rabbitmq_food_reference_import_queue: str = field(
        default_factory=lambda: getenv(
            "RABBITMQ_FOOD_REFERENCE_IMPORT_QUEUE",
            "foodsnap.food_reference_import",
        )
    )
    usda_fdc_api_key: str = field(default_factory=lambda: getenv("USDA_FDC_API_KEY", "DEMO_KEY"))
    usda_fdc_base_url: str = field(
        default_factory=lambda: getenv("USDA_FDC_BASE_URL", "https://api.nal.usda.gov/fdc/v1")
    )
    meal_classifier_backend: str = field(
        default_factory=lambda: getenv("MEAL_CLASSIFIER_BACKEND", "stub")
    )
    aws_region: str = field(default_factory=lambda: getenv("AWS_REGION", "us-east-1"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
