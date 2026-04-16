import asyncio
import logging
from typing import Any

from app.core.config import get_settings
from app.db.repositories.meals import MealRepository
from app.db.session import get_db_session, initialize_database
from app.services.calorie_estimator import CalorieEstimatorService
from app.services.meal_analysis import MealAnalysisService
from consumers.rabbitmq import run_consumer


logger = logging.getLogger(__name__)


def process_message(payload: dict[str, Any]) -> None:
    if payload.get("event_type") != "meal.analysis.requested":
        logger.warning("Ignoring unsupported event type: %s", payload.get("event_type"))
        return
    if payload.get("version") != 1:
        logger.warning("Ignoring unsupported event version: %s", payload.get("version"))
        return

    meal_id = payload.get("meal_id")
    if not isinstance(meal_id, str) or not meal_id:
        logger.warning("Ignoring meal-analysis message without meal_id")
        return

    try:
        with get_db_session() as session:
            service = MealAnalysisService(
                MealRepository(session),
                CalorieEstimatorService(session),
            )
            service.process_meal(meal_id)
    except Exception:
        logger.exception("Meal analysis failed for meal %s", meal_id)
        with get_db_session() as session:
            MealRepository(session).mark_failed(meal_id)
        raise


async def main() -> None:
    initialize_database()
    settings = get_settings()
    await run_consumer(
        queue_name=settings.rabbitmq_meal_analysis_queue,
        handler=process_message,
        service_name="meal-analysis-consumer",
    )


if __name__ == "__main__":
    asyncio.run(main())
