import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable


logger = logging.getLogger(__name__)


class InMemoryQueueService:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[str] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def _ensure_queue(self) -> asyncio.Queue[str]:
        loop = asyncio.get_running_loop()
        if self._queue is None or self._loop is not loop:
            self._queue = asyncio.Queue()
            self._loop = loop
        return self._queue

    async def enqueue_meal(self, meal_id: str) -> None:
        queue = self._ensure_queue()
        await queue.put(meal_id)
        logger.info("Queued meal %s for analysis", meal_id)

    async def dequeue_meal(self) -> str:
        queue = self._ensure_queue()
        meal_id = await queue.get()
        queue.task_done()
        return meal_id

    def start_worker(
        self, worker_factory: Callable[[], Awaitable[None]]
    ) -> asyncio.Task[None]:
        return asyncio.create_task(worker_factory())

    async def stop_worker(self, worker_task: asyncio.Task[None]) -> None:
        worker_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await worker_task


queue_service = InMemoryQueueService()
