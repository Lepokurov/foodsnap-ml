from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "storage": "local_stub",
        "queue": "in_memory",
        "persistence": "in_memory",
    }

