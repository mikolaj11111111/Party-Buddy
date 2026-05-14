from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel

from backend.app.models.timestamps import utc_now


class SessionMode(StrEnum):
    """Supported local session modes."""

    solo = "solo"
    hotseat = "hotseat"


class SessionStatus(StrEnum):
    """Lifecycle states for a stored game session."""

    in_progress = "in_progress"
    finished = "finished"


class Session(SQLModel, table=True):
    """Stored trivia session with MVP round and timer settings."""

    __tablename__ = "game_sessions"

    id: str = Field(
        default_factory=lambda: uuid4().hex,
        primary_key=True,
        max_length=64,
    )
    profile_id: str = Field(default="global", foreign_key="profiles.id", max_length=64)
    mode: SessionMode = Field(default=SessionMode.solo, index=True)
    status: SessionStatus = Field(default=SessionStatus.in_progress, index=True)
    total_rounds: int = Field(default=10, ge=1, le=100)
    round_seconds: int = Field(default=15, ge=1, le=300)
    current_round: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=utc_now)
    finished_at: datetime | None = None

    @field_validator("id", "profile_id")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """Reject empty session identifiers after trimming whitespace."""

        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @model_validator(mode="after")
    def validate_current_round(self) -> "Session":
        """Ensure current_round never points beyond total_rounds."""

        if self.current_round > self.total_rounds:
            raise ValueError("current_round must not exceed total_rounds")
        return self
