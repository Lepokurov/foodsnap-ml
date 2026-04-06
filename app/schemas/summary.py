from datetime import date

from pydantic import BaseModel


class DailySummaryResponse(BaseModel):
    date: date
    total_meals: int
    processed_meals: int
    total_estimated_calories: int

