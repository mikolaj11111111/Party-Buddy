from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from backend.app.models.timestamps import utc_now


class Profile(SQLModel, table=True):
    """Single local profile used to group game sessions in MVP."""

    __tablename__ = "profiles"

    id: str = Field(default="global", primary_key=True, max_length=64)
    display_name: str = Field(default="Player", max_length=64)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("id", "display_name")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """Reject empty profile identifiers and display names."""

        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value
