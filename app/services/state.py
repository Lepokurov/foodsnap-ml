from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class UserRecord:
    id: str
    email: str
    full_name: str
    password_hash: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MealRecord:
    id: str
    user_id: str
    status: str
    image_url: str
    image_storage: str
    created_at: datetime
    updated_at: datetime
    meal_timestamp: datetime
    recognized_label: str | None = None
    confidence: float | None = None
    estimated_calories: int | None = None


@dataclass
class PredictionRecord:
    meal_id: str
    raw_label: str
    normalized_label: str
    confidence: float
    model_version: str


class InMemoryStore:
    def __init__(self) -> None:
        self.users_by_id: dict[str, UserRecord] = {}
        self.users_by_email: dict[str, UserRecord] = {}
        self.tokens: dict[str, str] = {}
        self.meals: dict[str, MealRecord] = {}
        self.predictions: dict[str, PredictionRecord] = {}
        self.food_reference: dict[str, int] = {
            "burger": 550,
            "pizza": 700,
            "salad": 280,
            "pasta": 640,
            "sushi": 420,
            "steak": 610,
            "soup": 240,
            "unknown": 450,
        }


store = InMemoryStore()

