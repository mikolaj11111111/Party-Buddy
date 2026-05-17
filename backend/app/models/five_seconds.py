from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel


class FiveSecondsPrompt(SQLModel):
    """One prompt for the 5 Seconds game."""

    id: str = Field(max_length=64)
    category: str = Field(max_length=64)
    difficulty: str = Field(max_length=16)
    prompt: str
    expected_answer_count: int = Field(default=3, ge=1)
    sample_answers: list[str]

    @field_validator("id", "category", "difficulty", "prompt")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """Reject required text fields that become empty after trimming."""

        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("sample_answers")
    @classmethod
    def validate_sample_answers(cls, value: list[str]) -> list[str]:
        """Keep only non-empty example answers for future UI judging help."""

        cleaned_answers = [answer.strip() for answer in value if answer.strip()]
        if not cleaned_answers:
            raise ValueError("sample_answers must not be empty")
        return cleaned_answers

    @model_validator(mode="after")
    def validate_answer_count(self) -> "FiveSecondsPrompt":
        """Ensure the examples can satisfy the required answer count."""

        if len(self.sample_answers) < self.expected_answer_count:
            raise ValueError("sample_answers must cover expected_answer_count")
        return self
