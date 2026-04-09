from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps.auth import get_current_user
from app.db.models.user import User
from app.schemas.meal import MealCreateResponse, MealListResponse, MealResponse
from app.services.meal_ingestion import meal_ingestion_service


router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("", response_model=MealCreateResponse, status_code=status.HTTP_201_CREATED)
async def upload_meal(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
) -> MealCreateResponse:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is required.")
    return await meal_ingestion_service.create_meal(user, file)


@router.get("", response_model=MealListResponse)
def list_meals(user: User = Depends(get_current_user)) -> MealListResponse:
    return meal_ingestion_service.list_meals(user)


@router.get("/{meal_id}", response_model=MealResponse)
def get_meal(meal_id: str, user: User = Depends(get_current_user)) -> MealResponse:
    try:
        return meal_ingestion_service.get_meal(user, meal_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
