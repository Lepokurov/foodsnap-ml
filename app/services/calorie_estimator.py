from sqlalchemy import select

from app.db.models.food_reference import FoodReference
from app.db.session import get_db_session


class CalorieEstimatorService:
    def estimate(self, normalized_label: str) -> int:
        with get_db_session() as session:
            reference = session.scalar(
                select(FoodReference).where(FoodReference.label == normalized_label)
            )
            if reference is not None:
                return reference.estimated_calories

            fallback = session.get(FoodReference, "unknown")
            return fallback.estimated_calories if fallback is not None else 450


calorie_estimator_service = CalorieEstimatorService()
