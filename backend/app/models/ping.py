from datetime import datetime

from sqlmodel import Field, SQLModel

from backend.app.models.timestamps import utc_now


class Ping(SQLModel, table=True):
    """Temporary SQLite smoke-test table from M1."""

    id: int | None = Field(default=None, primary_key=True)
    message: str = Field(default="pong", max_length=64)
    created_at: datetime = Field(default_factory=utc_now)
