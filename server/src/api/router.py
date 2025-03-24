from fastapi import APIRouter

from src.api.v1.tasks import tasks_router


def setup_routes() -> APIRouter:
    """Configure and return the main API router with all routes."""
    router = APIRouter()
    router.include_router(tasks_router)
    return router
