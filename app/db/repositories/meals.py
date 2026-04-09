from datetime import datetime, timezone

from sqlalchemy import select

from app.db.models.meal_entry import MealEntry
from app.db.models.meal_prediction import MealPrediction
from app.db.session import get_db_session


class MealRepository:
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
        with get_db_session() as session:
            session.add(meal)
        return meal

    def get_for_user(self, *, meal_id: str, user_id: str) -> MealEntry | None:
        with get_db_session() as session:
            return session.scalar(
                select(MealEntry).where(
                    MealEntry.id == meal_id,
                    MealEntry.user_id == user_id,
                )
            )

    def list_for_user(self, *, user_id: str) -> list[MealEntry]:
        with get_db_session() as session:
            statement = (
                select(MealEntry)
                .where(MealEntry.user_id == user_id)
                .order_by(MealEntry.created_at.desc())
            )
            return list(session.scalars(statement))

    def get_by_id(self, meal_id: str) -> MealEntry | None:
        with get_db_session() as session:
            return session.get(MealEntry, meal_id)

    def mark_processing(self, meal_id: str) -> MealEntry | None:
        with get_db_session() as session:
            meal = session.get(MealEntry, meal_id)
            if meal is None:
                return None
            meal.status = "processing"
            meal.updated_at = datetime.now(timezone.utc)
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
        with get_db_session() as session:
            meal = session.get(MealEntry, meal_id)
            if meal is None:
                return None

            meal.status = "done"
            meal.recognized_label = recognized_label
            meal.confidence = confidence
            meal.estimated_calories = estimated_calories
            meal.updated_at = datetime.now(timezone.utc)

            prediction = session.get(MealPrediction, meal_id)
            if prediction is None:
                prediction = MealPrediction(
                    meal_id=meal_id,
                    raw_label=raw_label,
                    normalized_label=recognized_label,
                    confidence=confidence,
                    model_version=model_version,
                )
                session.add(prediction)
            else:
                prediction.raw_label = raw_label
                prediction.normalized_label = recognized_label
                prediction.confidence = confidence
                prediction.model_version = model_version

            return meal

    def mark_failed(self, meal_id: str) -> MealEntry | None:
        with get_db_session() as session:
            meal = session.get(MealEntry, meal_id)
            if meal is None:
                return None
            meal.status = "failed"
            meal.updated_at = datetime.now(timezone.utc)
            return meal
