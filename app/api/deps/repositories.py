from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.db.repositories.meals import MealRepository
from app.db.repositories.summaries import SummaryRepository
from app.db.repositories.users import UserRepository


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_meal_repository(db: Session = Depends(get_db)) -> MealRepository:
    return MealRepository(db)


def get_summary_repository(db: Session = Depends(get_db)) -> SummaryRepository:
    return SummaryRepository(db)
