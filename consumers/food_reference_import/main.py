import asyncio
import logging
from typing import Any

from app.core.config import get_settings
from app.db.session import get_db_session, initialize_database
from app.services.food_data_client import USDAFoodDataCentralClient
from app.services.food_reference_import import FoodReferenceImportService
from consumers.rabbitmq import run_consumer


logger = logging.getLogger(__name__)


def process_message(payload: dict[str, Any]) -> None:
    if payload.get("event_type") != "food_reference.import.requested":
        logger.warning("Ignoring unsupported event type: %s", payload.get("event_type"))
        return
    if payload.get("version") != 1:
        logger.warning("Ignoring unsupported event version: %s", payload.get("version"))
        return

    labels = payload.get("labels")
    if not isinstance(labels, list):
        logger.warning("Ignoring food-reference import message without labels")
        return

    source = str(payload.get("source", ""))
    if source != "usda_fdc":
        logger.warning("Ignoring unsupported food-reference source: %s", source)
        return

    with get_db_session() as session:
        imported_count = FoodReferenceImportService(
            session,
            USDAFoodDataCentralClient(),
        ).import_labels(
            source=str(payload.get("source", "")),
            labels=[label for label in labels if isinstance(label, str)],
            limit_per_label=int(payload.get("limit_per_label", 3)),
            mode=str(payload.get("mode", "upsert")),
        )

    logger.info(
        "Food-reference import %s completed with %s row(s)",
        payload.get("import_request_id"),
        imported_count,
    )


async def main() -> None:
    initialize_database()
    settings = get_settings()
    await run_consumer(
        queue_name=settings.rabbitmq_food_reference_import_queue,
        handler=process_message,
        service_name="food-reference-import-consumer",
    )


if __name__ == "__main__":
    asyncio.run(main())
