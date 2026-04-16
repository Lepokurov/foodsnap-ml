from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps.auth import get_current_user
from app.api.deps.queue import get_queue_service
from app.core.config import get_settings
from app.db.models.user import User
from app.schemas.food_reference import (
    FoodReferenceImportRequest,
    FoodReferenceImportResponse,
)
from app.services.queue import QueuePublishError, QueueService


router = APIRouter(prefix="/food-reference", tags=["food-reference"])


@router.post(
    "/imports",
    response_model=FoodReferenceImportResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_food_reference_import(
    payload: FoodReferenceImportRequest,
    user: User = Depends(get_current_user),
    queue: QueueService = Depends(get_queue_service),
) -> FoodReferenceImportResponse:
    try:
        message = await queue.enqueue_food_reference_import(
            source=payload.source,
            labels=payload.labels,
            requested_by_user_id=user.id,
            limit_per_label=payload.limit_per_label,
            mode=payload.mode,
        )
    except QueuePublishError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Food reference import task could not be queued.",
        ) from exc

    settings = get_settings()
    return FoodReferenceImportResponse(
        queued=True,
        event_type=message["event_type"],
        import_request_id=message["import_request_id"],
        queue=settings.rabbitmq_food_reference_import_queue,
        source=message["source"],
        labels=message["labels"],
        limit_per_label=message["limit_per_label"],
        mode=message["mode"],
    )
