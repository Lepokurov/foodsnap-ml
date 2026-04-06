from datetime import datetime, timezone

from fastapi import UploadFile

from app.schemas.meal import MealCreateResponse, MealListResponse, MealResponse
from app.services.queue import queue_service
from app.services.state import MealRecord, UserRecord, store
from app.services.storage import storage_service
from app.utils.ids import new_id


class MealIngestionService:
    async def create_meal(self, user: UserRecord, upload: UploadFile) -> MealCreateResponse:
        meal_id = new_id("meal")
        image_url = await storage_service.save_upload(meal_id, upload)
        timestamp = datetime.now(timezone.utc)

        meal = MealRecord(
            id=meal_id,
            user_id=user.id,
            status="pending",
            image_url=image_url,
            image_storage=storage_service.storage_name,
            created_at=timestamp,
            updated_at=timestamp,
            meal_timestamp=timestamp,
        )
        store.meals[meal.id] = meal
        await queue_service.enqueue_meal(meal.id)
        return MealCreateResponse(
            id=meal.id,
            status=meal.status,
            image_url=meal.image_url,
            queued=True,
        )

    def get_meal(self, user: UserRecord, meal_id: str) -> MealResponse:
        meal = store.meals.get(meal_id)
        if meal is None or meal.user_id != user.id:
            raise LookupError("Meal not found.")
        return self._to_schema(meal)

    def list_meals(self, user: UserRecord) -> MealListResponse:
        items = [
            self._to_schema(meal)
            for meal in sorted(
                store.meals.values(), key=lambda item: item.created_at, reverse=True
            )
            if meal.user_id == user.id
        ]
        return MealListResponse(items=items, total=len(items))

    @staticmethod
    def _to_schema(meal: MealRecord) -> MealResponse:
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

