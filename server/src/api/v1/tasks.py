from fastcrud import EndpointCreator

from src.core.database import get_session
from src.models.tasks import (
    Task,
    TaskCreate,
    TaskUpdate,
)

tasks_endpoint = EndpointCreator(
    session=get_session,
    model=Task,
    path="/tasks",
    tags=["tasks"],
    create_schema=TaskCreate,
    update_schema=TaskUpdate,
    is_deleted_column='deleted',
)

tasks_endpoint.add_routes_to_router()
tasks_router = tasks_endpoint.router



