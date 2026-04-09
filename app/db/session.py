from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.db.models import FoodReference, MealEntry, MealPrediction, User

DEFAULT_FOOD_REFERENCE = {
    "burger": 550,
    "pizza": 700,
    "salad": 280,
    "pasta": 640,
    "sushi": 420,
    "steak": 610,
    "soup": 240,
    "unknown": 450,
}


def _engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, **_engine_kwargs(settings.database_url))


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


@contextmanager
def get_db_session() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def initialize_database() -> None:
    Base.metadata.create_all(bind=get_engine())
    seed_food_reference()


def reset_database() -> None:
    Base.metadata.drop_all(bind=get_engine())
    Base.metadata.create_all(bind=get_engine())
    seed_food_reference()


def dispose_database() -> None:
    engine = get_engine()
    get_session_factory.cache_clear()
    get_engine.cache_clear()
    engine.dispose()


def seed_food_reference() -> None:
    with get_db_session() as session:
        existing_labels = set(session.scalars(select(FoodReference.label)))
        for label, estimated_calories in DEFAULT_FOOD_REFERENCE.items():
            if label in existing_labels:
                continue
            session.add(
                FoodReference(label=label, estimated_calories=estimated_calories)
            )


def check_database_connection() -> bool:
    try:
        with get_engine().connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return True
    except SQLAlchemyError:
        return False
