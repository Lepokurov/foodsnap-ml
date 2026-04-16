from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import boto3

from app.core.config import get_settings
from app.db.models.meal_entry import MealEntry


@dataclass(frozen=True)
class MealImage:
    source_uri: str
    storage: str
    object_name: str
    content: bytes | None = None
    s3_bucket: str | None = None
    s3_key: str | None = None


class MealImageLoader:
    def load(self, meal: MealEntry) -> MealImage:
        s3_location = self._parse_s3_location(meal.image_url)
        if meal.image_storage in {"s3", "aws_s3"} or s3_location is not None:
            bucket, key = s3_location or self._parse_s3_location_or_raise(meal.image_url)
            content = self._download_s3_object(bucket=bucket, key=key)
            return MealImage(
                source_uri=meal.image_url,
                storage="s3",
                object_name=Path(key).name,
                content=content,
                s3_bucket=bucket,
                s3_key=key,
            )

        path = Path(meal.image_url)
        return MealImage(
            source_uri=meal.image_url,
            storage=meal.image_storage,
            object_name=path.name,
            content=path.read_bytes(),
        )

    def _download_s3_object(self, *, bucket: str, key: str) -> bytes:
        settings = get_settings()
        client = boto3.client("s3", region_name=settings.aws_region)
        response = client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()

    @staticmethod
    def _parse_s3_location(uri: str) -> tuple[str, str] | None:
        parsed = urlparse(uri)
        if parsed.scheme == "s3" and parsed.netloc and parsed.path:
            return parsed.netloc, parsed.path.lstrip("/")

        host_parts = parsed.netloc.split(".")
        if parsed.scheme in {"http", "https"} and len(host_parts) >= 4:
            is_s3_host = host_parts[1] == "s3" or host_parts[0].endswith("s3")
            if is_s3_host and parsed.path:
                return host_parts[0], parsed.path.lstrip("/")

        return None

    @classmethod
    def _parse_s3_location_or_raise(cls, uri: str) -> tuple[str, str]:
        location = cls._parse_s3_location(uri)
        if location is None:
            raise ValueError(f"Could not parse S3 location from image URL: {uri}")
        return location
