from datetime import date

from app.schemas.summary import DailySummaryResponse
from app.services.state import UserRecord, store
from app.utils.datetime import same_utc_day


class SummaryService:
    def get_daily_summary(self, user: UserRecord, requested_date: date) -> DailySummaryResponse:
        meals = [
            meal
            for meal in store.meals.values()
            if meal.user_id == user.id and same_utc_day(meal.meal_timestamp, requested_date)
        ]
        processed_meals = [meal for meal in meals if meal.status == "done"]
        total_calories = sum(meal.estimated_calories or 0 for meal in processed_meals)
        return DailySummaryResponse(
            date=requested_date,
            total_meals=len(meals),
            processed_meals=len(processed_meals),
            total_estimated_calories=total_calories,
        )


summary_service = SummaryService()

