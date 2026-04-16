from datetime import date

from app.db.models.user import User
from app.db.repositories.summaries import SummaryRepository
from app.schemas.summary import DailySummaryResponse


class SummaryService:
    def __init__(self, summaries: SummaryRepository) -> None:
        self._summaries = summaries

    def get_daily_summary(self, user: User, requested_date: date) -> DailySummaryResponse:
        summary = self._summaries.get_daily_summary(
            user_id=user.id,
            requested_date=requested_date,
        )
        return DailySummaryResponse(
            date=requested_date,
            total_meals=summary["total_meals"],
            processed_meals=summary["processed_meals"],
            total_estimated_calories=summary["total_estimated_calories"],
        )
