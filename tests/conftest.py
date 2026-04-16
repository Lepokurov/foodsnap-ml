import os
from pathlib import Path

import pytest

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./data/test.db"
os.environ["QUEUE_BACKEND"] = "in_memory"

from app.core.config import get_settings
from app.api.deps.queue import get_queue_service
from app.db.session import dispose_database, reset_database


@pytest.fixture(autouse=True)
def reset_db() -> None:
    test_db_path = Path("data/test.db")
    test_db_path.parent.mkdir(parents=True, exist_ok=True)
    get_settings.cache_clear()
    get_queue_service.cache_clear()
    dispose_database()
    reset_database()
    yield
    get_queue_service.cache_clear()
    dispose_database()
