from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps.auth import get_current_user
from app.api.deps.queue import get_queue_service
from app.api.deps.services import get_meal_ingestion_service
from app.db.models.user import User
from app.schemas.meal import MealCreateResponse, MealListResponse, MealResponse
from app.services.meal_ingestion import MealIngestionService
from app.services.queue import QueuePublishError, QueueService


router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("", response_model=MealCreateResponse, status_code=status.HTTP_201_CREATED)
async def upload_meal(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    queue: QueueService = Depends(get_queue_service),
    meals: MealIngestionService = Depends(get_meal_ingestion_service),
) -> MealCreateResponse:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is required.")
    try:
        return await meals.create_meal(user, file, queue)
    except QueuePublishError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Meal was saved, but queue publishing failed.",
        ) from exc


@router.get("", response_model=MealListResponse)
def list_meals(
    user: User = Depends(get_current_user),
    meals: MealIngestionService = Depends(get_meal_ingestion_service),
) -> MealListResponse:
    return meals.list_meals(user)


@router.get("/{meal_id}", response_model=MealResponse)
def get_meal(
    meal_id: str,
    user: User = Depends(get_current_user),
    meals: MealIngestionService = Depends(get_meal_ingestion_service),
) -> MealResponse:
    try:
        return meals.get_meal(user, meal_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
