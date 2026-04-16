import asyncio
import json
import logging
from collections.abc import Callable, Awaitable
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.core.config import get_settings
from app.core.logging import configure_logging


logger = logging.getLogger(__name__)

MessageHandler = Callable[[dict[str, Any]], Awaitable[None] | None]


async def run_consumer(
    *,
    queue_name: str,
    handler: MessageHandler,
    service_name: str,
) -> None:
    configure_logging()
    settings = get_settings()
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(queue_name, durable=True)

        logger.info("%s consuming queue %s", service_name, queue_name)
        await queue.consume(lambda message: _handle_message(message, handler))
        await asyncio.Future()


async def _handle_message(
    message: AbstractIncomingMessage,
    handler: MessageHandler,
) -> None:
    async with message.process(requeue=False):
        try:
            payload = json.loads(message.body.decode("utf-8"))
        except json.JSONDecodeError:
            logger.warning("Discarding invalid JSON message")
            return

        if not isinstance(payload, dict):
            logger.warning("Discarding non-object JSON message")
            return

        result = handler(payload)
        if result is not None:
            await result
