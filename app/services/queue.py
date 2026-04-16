import json
import logging
from datetime import datetime, timezone
from typing import Any, Protocol

import aio_pika
from aio_pika import DeliveryMode, Message

from app.core.config import get_settings
from app.utils.ids import new_id


logger = logging.getLogger(__name__)


class QueuePublishError(RuntimeError):
    pass


class QueueService(Protocol):
    async def enqueue_meal(self, meal_id: str) -> None: ...

    async def enqueue_food_reference_import(
        self,
        *,
        source: str,
        labels: list[str],
        requested_by_user_id: str,
        limit_per_label: int,
        mode: str,
    ) -> dict[str, Any]: ...

    async def close(self) -> None: ...


def build_meal_analysis_message(meal_id: str) -> dict[str, Any]:
    return {
        "event_type": "meal.analysis.requested",
        "version": 1,
        "meal_id": meal_id,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }


def build_food_reference_import_message(
    *,
    source: str,
    labels: list[str],
    requested_by_user_id: str,
    limit_per_label: int,
    mode: str,
) -> dict[str, Any]:
    return {
        "event_type": "food_reference.import.requested",
        "version": 1,
        "import_request_id": new_id("food_import"),
        "source": source,
        "labels": labels,
        "limit_per_label": limit_per_label,
        "mode": mode,
        "requested_by_user_id": requested_by_user_id,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }


class InMemoryQueueService:
    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []

    async def enqueue_meal(self, meal_id: str) -> None:
        message = build_meal_analysis_message(meal_id)
        self.messages.append(message)
        logger.info("Queued meal %s for analysis in memory", meal_id)

    async def enqueue_food_reference_import(
        self,
        *,
        source: str,
        labels: list[str],
        requested_by_user_id: str,
        limit_per_label: int,
        mode: str,
    ) -> dict[str, Any]:
        message = build_food_reference_import_message(
            source=source,
            labels=labels,
            requested_by_user_id=requested_by_user_id,
            limit_per_label=limit_per_label,
            mode=mode,
        )
        self.messages.append(message)
        logger.info(
            "Queued food reference import %s in memory",
            message["import_request_id"],
        )
        return message

    async def close(self) -> None:
        return None


class RabbitMQQueueService:
    def __init__(self) -> None:
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractRobustChannel | None = None

    async def enqueue_meal(self, meal_id: str) -> None:
        settings = get_settings()
        payload = build_meal_analysis_message(meal_id)
        try:
            await self._publish(
                queue_name=settings.rabbitmq_meal_analysis_queue,
                payload=payload,
            )
        except Exception as exc:
            raise QueuePublishError("Could not publish meal analysis task.") from exc
        logger.info(
            "Published meal %s to RabbitMQ queue %s",
            meal_id,
            settings.rabbitmq_meal_analysis_queue,
        )

    async def enqueue_food_reference_import(
        self,
        *,
        source: str,
        labels: list[str],
        requested_by_user_id: str,
        limit_per_label: int,
        mode: str,
    ) -> dict[str, Any]:
        settings = get_settings()
        payload = build_food_reference_import_message(
            source=source,
            labels=labels,
            requested_by_user_id=requested_by_user_id,
            limit_per_label=limit_per_label,
            mode=mode,
        )
        try:
            await self._publish(
                queue_name=settings.rabbitmq_food_reference_import_queue,
                payload=payload,
            )
        except Exception as exc:
            raise QueuePublishError(
                "Could not publish food reference import task."
            ) from exc
        logger.info(
            "Published food reference import %s to RabbitMQ queue %s",
            payload["import_request_id"],
            settings.rabbitmq_food_reference_import_queue,
        )
        return payload

    async def _publish(self, *, queue_name: str, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        channel = await self._get_channel()
        await channel.declare_queue(queue_name, durable=True)
        await channel.default_exchange.publish(
            Message(
                body=body,
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
                headers={
                    "event_type": payload["event_type"],
                    "version": str(payload["version"]),
                },
            ),
            routing_key=queue_name,
        )

    async def _get_channel(self) -> aio_pika.abc.AbstractRobustChannel:
        settings = get_settings()
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)

        if self._channel is None or self._channel.is_closed:
            self._channel = await self._connection.channel()

        return self._channel

    async def close(self) -> None:
        if self._channel is not None and not self._channel.is_closed:
            await self._channel.close()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()


def create_queue_service() -> QueueService:
    settings = get_settings()
    if settings.queue_backend == "in_memory":
        return InMemoryQueueService()
    if settings.queue_backend == "rabbitmq":
        return RabbitMQQueueService()
    raise ValueError(f"Unsupported queue backend: {settings.queue_backend}")

