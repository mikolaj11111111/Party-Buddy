from typing import Literal

from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel

AnswerLetter = Literal["A", "B", "C", "D"]
Difficulty = Literal["easy", "medium", "hard"]

EXPECTED_OPTION_KEYS = {"A", "B", "C", "D"}


class Question(SQLModel):
    id: str
    category: str
    difficulty: Difficulty
    question: str
    options: dict[AnswerLetter, str]
    correct_answer: AnswerLetter
    explanation: str | None = None
    aliases: dict[AnswerLetter, list[str]] = Field(default_factory=dict)

    @field_validator("id", "category", "question")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("options")
    @classmethod
    def validate_options(
        cls, value: dict[AnswerLetter, str]
    ) -> dict[AnswerLetter, str]:
        if set(value) != EXPECTED_OPTION_KEYS:
            raise ValueError("options must contain exactly A, B, C and D")

        normalized_options: dict[AnswerLetter, str] = {}
        for key, option in value.items():
            option = option.strip()
            if not option:
                raise ValueError(f"option {key} must not be empty")
            normalized_options[key] = option

        return normalized_options

    @field_validator("aliases")
    @classmethod
    def validate_aliases(
        cls, value: dict[AnswerLetter, list[str]]
    ) -> dict[AnswerLetter, list[str]]:
        invalid_keys = set(value) - EXPECTED_OPTION_KEYS
        if invalid_keys:
            raise ValueError("aliases keys must be one of A, B, C or D")

        normalized_aliases: dict[AnswerLetter, list[str]] = {}
        for key, aliases in value.items():
            cleaned_aliases = [alias.strip() for alias in aliases if alias.strip()]
            if cleaned_aliases:
                normalized_aliases[key] = cleaned_aliases

        return normalized_aliases

    @model_validator(mode="after")
    def validate_correct_answer_option(self) -> "Question":
        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must point to an existing option")
        return self
