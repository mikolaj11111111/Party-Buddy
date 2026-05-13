from typing import Literal

from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel

from backend.app.models.question import AnswerLetter

InputMethod = Literal["click", "voice", "text"]


class AnswerRequest(SQLModel):
    question_id: str
    input_method: InputMethod
    answer_letter: AnswerLetter | None = None
    answer_text: str | None = None

    @field_validator("question_id")
    @classmethod
    def validate_question_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question_id must not be empty")
        return value

    @field_validator("answer_letter", mode="before")
    @classmethod
    def normalize_answer_letter(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip().upper()
        return value or None

    @field_validator("answer_text", mode="before")
    @classmethod
    def normalize_answer_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_answer_payload(self) -> "AnswerRequest":
        if self.answer_letter is None and self.answer_text is None:
            raise ValueError("answer_letter or answer_text is required")
        return self


class AnswerResponse(SQLModel):
    question_id: str
    submitted_answer: str
    matched_answer: AnswerLetter | None = None
    is_correct: bool
    correct_answer: AnswerLetter
    explanation: str | None = None
    score_delta: int = Field(ge=0)

    @field_validator("question_id", "submitted_answer")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value
