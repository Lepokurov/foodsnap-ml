from datetime import datetime, timezone

from fastapi import UploadFile

from app.db.models.meal_entry import MealEntry
from app.db.models.user import User
from app.db.repositories.meals import MealRepository
from app.schemas.meal import MealCreateResponse, MealListResponse, MealResponse
from app.services.queue import queue_service
from app.services.storage import storage_service
from app.utils.ids import new_id


class MealIngestionService:
    def __init__(self) -> None:
        self._meals = MealRepository()

    async def create_meal(self, user: User, upload: UploadFile) -> MealCreateResponse:
        meal_id = new_id("meal")
        image_url = await storage_service.save_upload(meal_id, upload)
        timestamp = datetime.now(timezone.utc)

        meal = self._meals.create(
            id=meal_id,
            user_id=user.id,
            status="pending",
            image_url=image_url,
            image_storage=storage_service.storage_name,
            meal_timestamp=timestamp,
        )
        await queue_service.enqueue_meal(meal.id)
        return MealCreateResponse(
            id=meal.id,
            status=meal.status,
            image_url=meal.image_url,
            queued=True,
        )

    def get_meal(self, user: User, meal_id: str) -> MealResponse:
        meal = self._meals.get_for_user(meal_id=meal_id, user_id=user.id)
        if meal is None:
            raise LookupError("Meal not found.")
        return self._to_schema(meal)

    def list_meals(self, user: User) -> MealListResponse:
        meals = self._meals.list_for_user(user_id=user.id)
        items = [self._to_schema(meal) for meal in meals]
        return MealListResponse(items=items, total=len(items))

    @staticmethod
    def _to_schema(meal: MealEntry) -> MealResponse:
        return MealResponse(
            id=meal.id,
            user_id=meal.user_id,
            status=meal.status,
            image_url=meal.image_url,
            image_storage=meal.image_storage,
            created_at=meal.created_at,
            updated_at=meal.updated_at,
            meal_timestamp=meal.meal_timestamp,
            recognized_label=meal.recognized_label,
            confidence=meal.confidence,
            estimated_calories=meal.estimated_calories,
        )


meal_ingestion_service = MealIngestionService()
