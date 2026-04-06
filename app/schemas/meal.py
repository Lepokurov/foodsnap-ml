from datetime import datetime
from typing import Literal

from pydantic import BaseModel


MealStatus = Literal["pending", "processing", "done", "failed"]


class MealCreateResponse(BaseModel):
    id: str
    status: MealStatus
    image_url: str
    queued: bool


class MealResponse(BaseModel):
    id: str
    user_id: str
    status: MealStatus
    image_url: str
    image_storage: str
    created_at: datetime
    updated_at: datetime
    meal_timestamp: datetime
    recognized_label: str | None = None
    confidence: float | None = None
    estimated_calories: int | None = None


class MealListResponse(BaseModel):
    items: list[MealResponse]
    total: int

