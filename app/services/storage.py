from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings
from app.utils.ids import build_upload_filename


class LocalStubStorageService:
    storage_name = "local_stub"

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


storage_service = LocalStubStorageService()
