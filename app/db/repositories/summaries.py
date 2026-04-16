from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.meal_entry import MealEntry


class SummaryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_daily_summary(self, *, user_id: str, requested_date: date) -> dict[str, int]:
        start_of_day = datetime.combine(requested_date, time.min, tzinfo=timezone.utc)
        end_of_day = start_of_day + timedelta(days=1)

        total_meals = self._session.scalar(
            select(func.count(MealEntry.id)).where(
                MealEntry.user_id == user_id,
                MealEntry.meal_timestamp >= start_of_day,
                MealEntry.meal_timestamp < end_of_day,
            )
        ) or 0

        processed_meals = self._session.scalar(
            select(func.count(MealEntry.id)).where(
                MealEntry.user_id == user_id,
                MealEntry.meal_timestamp >= start_of_day,
                MealEntry.meal_timestamp < end_of_day,
                MealEntry.status == "done",
            )
        ) or 0

        total_estimated_calories = self._session.scalar(
            select(func.coalesce(func.sum(MealEntry.estimated_calories), 0)).where(
                MealEntry.user_id == user_id,
                MealEntry.meal_timestamp >= start_of_day,
                MealEntry.meal_timestamp < end_of_day,
                MealEntry.status == "done",
            )
        ) or 0

        return {
            "total_meals": int(total_meals),
            "processed_meals": int(processed_meals),
            "total_estimated_calories": int(total_estimated_calories),
        }
