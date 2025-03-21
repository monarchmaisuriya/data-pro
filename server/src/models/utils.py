from pydantic import BaseModel


class ServerStatusResponse(BaseModel):
    name: str
    status: str
    database: str
    version: str
    environment: str
    error: str | None = None
