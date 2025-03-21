from datetime import datetime
from enum import Enum, IntEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


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
    due_date: datetime | None = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now})
    completed_at: datetime | None = Field(default=None, nullable=True)
    deleted: bool = Field(default=False, nullable=True)
    deleted_at: datetime | None = Field(default=None, nullable=True)
    status: TaskStatus = Field(default=TaskStatus.PENDING)


