from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.food_reference import FoodReference


class CalorieEstimatorService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def estimate(self, normalized_label: str) -> int:
        reference = self._session.scalar(
            select(FoodReference).where(FoodReference.label == normalized_label)
        )
        if reference is not None:
            return reference.estimated_calories

        fallback = self._session.get(FoodReference, "unknown")
        return fallback.estimated_calories if fallback is not None else 450
