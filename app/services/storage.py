from pathlib import Path
from typing import Protocol

import boto3
from fastapi import UploadFile

from app.core.config import get_settings
from app.utils.ids import build_upload_filename


class StorageService(Protocol):
    storage_name: str

    async def save_upload(self, meal_id: str, upload: UploadFile) -> str: ...


class LocalStubStorageService:
    storage_name = "local"

    async def save_upload(self, meal_id: str, upload: UploadFile) -> str:
        settings = get_settings()
        settings.local_upload_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(upload.filename or "meal.jpg").suffix or ".bin"
        original_stem = Path(upload.filename or "meal").stem
        file_name = build_upload_filename(meal_id, original_stem, suffix)
        destination = settings.local_upload_dir / file_name

        content = await upload.read()
        destination.write_bytes(content)
        await upload.seek(0)
        return str(destination)


class S3StorageService:
    storage_name = "s3"

    async def save_upload(self, meal_id: str, upload: UploadFile) -> str:
        settings = get_settings()
        if not settings.s3_bucket_name:
            raise ValueError("S3_BUCKET_NAME is required when STORAGE_BACKEND=s3.")

        suffix = Path(upload.filename or "meal.jpg").suffix or ".bin"
        original_stem = Path(upload.filename or "meal").stem
        file_name = build_upload_filename(meal_id, original_stem, suffix)
        key = "/".join(
            part.strip("/")
            for part in (settings.s3_upload_prefix, file_name)
            if part.strip("/")
        )

        content = await upload.read()
        await upload.seek(0)

        client = boto3.client("s3", region_name=settings.aws_region)
        extra_args = {"ContentType": upload.content_type or "application/octet-stream"}
        # todo: fix sync put
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=content,
            **extra_args,
        )
        return f"s3://{settings.s3_bucket_name}/{key}"


def create_storage_service() -> StorageService:
    settings = get_settings()
    if settings.storage_backend == "local":
        return LocalStubStorageService()
    if settings.storage_backend == "s3":
        return S3StorageService()
    raise ValueError(f"Unsupported storage backend: {settings.storage_backend}")
