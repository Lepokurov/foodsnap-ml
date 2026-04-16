from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.db.session import get_db_session


def get_db() -> Iterator[Session]:
    with get_db_session() as session:
        yield session
