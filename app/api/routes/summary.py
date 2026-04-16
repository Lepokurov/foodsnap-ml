from datetime import date

from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_user
from app.api.deps.common import parse_requested_date
from app.api.deps.services import get_summary_service
from app.db.models.user import User
from app.schemas.summary import DailySummaryResponse
from app.services.summary import SummaryService


router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/daily", response_model=DailySummaryResponse)
def daily_summary(
    requested_date: date | None = None,
    user: User = Depends(get_current_user),
    summaries: SummaryService = Depends(get_summary_service),
) -> DailySummaryResponse:
    return summaries.get_daily_summary(user, parse_requested_date(requested_date))
