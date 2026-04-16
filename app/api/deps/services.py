from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.api.deps.repositories import (
    get_meal_repository,
    get_summary_repository,
    get_user_repository,
)
from app.db.repositories.meals import MealRepository
from app.db.repositories.summaries import SummaryRepository
from app.db.repositories.users import UserRepository
from app.services.auth import AuthService
from app.services.calorie_estimator import CalorieEstimatorService
from app.services.meal_analysis import MealAnalysisService
from app.services.meal_ingestion import MealIngestionService
from app.services.summary import SummaryService


def get_auth_service(
    users: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(users)


def get_calorie_estimator_service(
    db: Session = Depends(get_db),
) -> CalorieEstimatorService:
    return CalorieEstimatorService(db)


def get_meal_ingestion_service(
    meals: MealRepository = Depends(get_meal_repository),
) -> MealIngestionService:
    return MealIngestionService(meals)


def get_meal_analysis_service(
    meals: MealRepository = Depends(get_meal_repository),
    calorie_estimator: CalorieEstimatorService = Depends(get_calorie_estimator_service),
) -> MealAnalysisService:
    return MealAnalysisService(meals, calorie_estimator)


def get_summary_service(
    summaries: SummaryRepository = Depends(get_summary_repository),
) -> SummaryService:
    return SummaryService(summaries)
