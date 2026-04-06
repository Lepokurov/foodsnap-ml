from datetime import date

from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_user
from app.api.deps.common import parse_requested_date
from app.schemas.summary import DailySummaryResponse
from app.services.state import UserRecord
from app.services.summary import summary_service


router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/daily", response_model=DailySummaryResponse)
def daily_summary(
    requested_date: date | None = None,
    user: UserRecord = Depends(get_current_user),
) -> DailySummaryResponse:
    return summary_service.get_daily_summary(user, parse_requested_date(requested_date))

