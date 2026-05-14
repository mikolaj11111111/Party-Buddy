from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from backend.app.models.timestamps import utc_now


class Score(SQLModel, table=True):
    """Stored per-player score for one finished or active session."""

    __tablename__ = "scores"

    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="game_sessions.id", max_length=64)
    player_id: str = Field(max_length=64)
    player_name: str = Field(max_length=64)
    player_order: int = Field(ge=0)
    score: int = Field(default=0, ge=0)
    correct_answers: int = Field(default=0, ge=0)
    answered_questions: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("session_id", "player_id", "player_name")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """Reject empty score identifiers and player names."""

        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value
