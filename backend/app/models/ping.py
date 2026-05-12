from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class Ping(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    message: str = Field(default="pong", max_length=64)
    created_at: datetime = Field(default_factory=utc_now)
