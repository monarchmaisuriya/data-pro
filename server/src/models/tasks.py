from datetime import datetime
from enum import Enum, IntEnum
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from src.models import SQLModel


class TaskPriority(IntEnum):
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    description: str|None = Field(default=None, nullable=True)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    parameters: dict = Field(default_factory=dict, sa_type=JSONB)
    result: dict = Field(default_factory=dict, sa_type=JSONB)
    due_date: datetime | None = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now})
    completed_at: datetime | None = Field(default=None, nullable=True)
    deleted: bool = Field(default=False, nullable=True)
    deleted_at: datetime | None = Field(default=None, nullable=True)

class TaskCreate(SQLModel):
    title: str
    description: str | None
    priority: TaskPriority
    parameters: dict
    due_date: datetime | None

class TaskRead(SQLModel):
    id: UUID
    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    parameters: dict
    result: dict
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    deleted: bool
    deleted_at: datetime | None

class TaskUpdate(SQLModel):
    title: str | None
    description: str | None
    priority: TaskPriority | None
    status: TaskStatus | None
    parameters: dict | None
    result: dict | None
    due_date: datetime | None

class TaskDelete(SQLModel):
    deleted: bool
    deleted_at: datetime

