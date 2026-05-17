import re

from pydantic import field_validator
from sqlmodel import Field, SQLModel

WORD_PATTERN = re.compile(r"^[a-ząćęłńóśźż ]+$")


class HangmanWord(SQLModel):
    """One word entry for the Hangman game."""

    id: str = Field(max_length=64)
    category: str = Field(max_length=64)
    difficulty: str = Field(max_length=16)
    word: str
    hint: str

    @field_validator("id", "category", "difficulty", "hint")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """Reject required text fields that become empty after trimming."""

        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("word")
    @classmethod
    def validate_word(cls, value: str) -> str:
        """Keep Hangman words lowercase and letter-only for simple guessing."""

        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("must not be empty")

        if not WORD_PATTERN.fullmatch(value):
            raise ValueError(
                "word must contain only lowercase Polish letters and spaces"
            )

        if len(value.replace(" ", "")) < 3:
            raise ValueError("word must have at least three letters")

        return value
