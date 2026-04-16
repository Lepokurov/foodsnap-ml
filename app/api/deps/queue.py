from functools import lru_cache

from app.services.queue import QueueService, create_queue_service


@lru_cache
def get_queue_service() -> QueueService:
    return create_queue_service()
