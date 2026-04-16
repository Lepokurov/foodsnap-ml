from functools import lru_cache

from app.services.storage import StorageService, create_storage_service


@lru_cache
def get_storage_service() -> StorageService:
    return create_storage_service()
