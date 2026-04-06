from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.meals import router as meals_router
from app.api.routes.summary import router as summary_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.queue import queue_service
from app.workers.meal_analysis_worker import meal_analysis_worker


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    worker_task = queue_service.start_worker(meal_analysis_worker.run_forever)
    try:
        yield
    finally:
        await queue_service.stop_worker(worker_task)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(meals_router, prefix=settings.api_prefix)
    app.include_router(summary_router, prefix=settings.api_prefix)

    return app


app = create_app()

