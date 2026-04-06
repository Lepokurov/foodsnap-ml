import asyncio
import logging

from app.services.meal_analysis import meal_analysis_service
from app.services.queue import queue_service


logger = logging.getLogger(__name__)


class MealAnalysisWorker:
    async def run_forever(self) -> None:
        while True:
            meal_id = await queue_service.dequeue_meal()
            try:
                await asyncio.sleep(0.05)
                meal_analysis_service.process_meal(meal_id)
                logger.info("Processed meal %s", meal_id)
            except Exception:
                logger.exception("Meal processing failed for %s", meal_id)


meal_analysis_worker = MealAnalysisWorker()

