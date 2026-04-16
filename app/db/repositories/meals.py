from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.meal_entry import MealEntry
from app.db.models.meal_prediction import MealPrediction


class MealRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        id: str,
        user_id: str,
        status: str,
        image_url: str,
        image_storage: str,
        meal_timestamp: datetime,
    ) -> MealEntry:
        timestamp = datetime.now(timezone.utc)
        meal = MealEntry(
            id=id,
            user_id=user_id,
            status=status,
            image_url=image_url,
            image_storage=image_storage,
            created_at=timestamp,
            updated_at=timestamp,
            meal_timestamp=meal_timestamp,
        )
        self._session.add(meal)
        self._session.flush()
        return meal

    def get_for_user(self, *, meal_id: str, user_id: str) -> MealEntry | None:
        return self._session.scalar(
            select(MealEntry).where(
                MealEntry.id == meal_id,
                MealEntry.user_id == user_id,
            )
        )

    def list_for_user(self, *, user_id: str) -> list[MealEntry]:
        statement = (
            select(MealEntry)
            .where(MealEntry.user_id == user_id)
            .order_by(MealEntry.created_at.desc())
        )
        return list(self._session.scalars(statement))

    def get_by_id(self, meal_id: str) -> MealEntry | None:
        return self._session.get(MealEntry, meal_id)

    def mark_processing(self, meal_id: str) -> MealEntry | None:
        meal = self._session.get(MealEntry, meal_id)
        if meal is None:
            return None
        meal.status = "processing"
        meal.updated_at = datetime.now(timezone.utc)
        self._session.flush()
        return meal

    def complete(
        self,
        *,
        meal_id: str,
        recognized_label: str,
        confidence: float,
        estimated_calories: int,
        raw_label: str,
        model_version: str,
    ) -> MealEntry | None:
        meal = self._session.get(MealEntry, meal_id)
        if meal is None:
            return None

        meal.status = "done"
        meal.recognized_label = recognized_label
        meal.confidence = confidence
        meal.estimated_calories = estimated_calories
        meal.updated_at = datetime.now(timezone.utc)

        prediction = self._session.get(MealPrediction, meal_id)
        if prediction is None:
            prediction = MealPrediction(
                meal_id=meal_id,
                raw_label=raw_label,
                normalized_label=recognized_label,
                confidence=confidence,
                model_version=model_version,
            )
            self._session.add(prediction)
        else:
            prediction.raw_label = raw_label
            prediction.normalized_label = recognized_label
            prediction.confidence = confidence
            prediction.model_version = model_version

        self._session.flush()
        return meal

    def mark_failed(self, meal_id: str) -> MealEntry | None:
        meal = self._session.get(MealEntry, meal_id)
        if meal is None:
            return None
        meal.status = "failed"
        meal.updated_at = datetime.now(timezone.utc)
        self._session.flush()
        return meal
