from datetime import datetime
from typing import Literal, TypeAlias

from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel

from backend.app.models.answer import InputMethod
from backend.app.models.question import AnswerLetter

GameInputMethod: TypeAlias = Literal["click", "voice", "text", "timeout"]


class GameStartSessionMessage(SQLModel):
    """Client message that starts one local trivia session."""

    type: Literal["start_session"]
    players: list[str]
    categories: list[str] | None = None
    round_count: int = Field(default=10, ge=1, le=100)
    round_seconds: int = Field(default=15, ge=1, le=300)

    @field_validator("players")
    @classmethod
    def validate_players(cls, value: list[str]) -> list[str]:
        """Trim player names and reject an empty player list."""

        players = [player.strip() for player in value if player.strip()]
        if not players:
            raise ValueError("players must contain at least one name")
        return players

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, value: list[str] | None) -> list[str] | None:
        """Trim optional category filters before question selection."""

        if value is None:
            return None

        categories = [category.strip() for category in value if category.strip()]
        return categories or None


class GameSubmitAnswerMessage(SQLModel):
    """Client message that submits an answer for the active question."""

    type: Literal["submit_answer"]
    question_id: str
    input_method: InputMethod
    answer_letter: AnswerLetter | None = None
    answer_text: str | None = None

    @field_validator("question_id")
    @classmethod
    def validate_question_id(cls, value: str) -> str:
        """Reject empty question identifiers."""

        value = value.strip()
        if not value:
            raise ValueError("question_id must not be empty")
        return value

    @field_validator("answer_letter", mode="before")
    @classmethod
    def normalize_answer_letter(cls, value: str | None) -> str | None:
        """Normalize optional answer letters to uppercase ABCD values."""

        if value is None:
            return None

        value = value.strip().upper()
        return value or None

    @field_validator("answer_text", mode="before")
    @classmethod
    def normalize_answer_text(cls, value: str | None) -> str | None:
        """Trim optional text answers before judging."""

        if value is None:
            return None

        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_answer_payload(self) -> "GameSubmitAnswerMessage":
        """Require at least one answer representation."""

        if self.answer_letter is None and self.answer_text is None:
            raise ValueError("answer_letter or answer_text is required")
        return self


class GamePlayerPayload(SQLModel):
    """Public player data sent to the frontend."""

    player_id: str
    player_name: str


class GameQuestionPayload(SQLModel):
    """Public question payload without the correct answer."""

    id: str
    category: str
    difficulty: str
    question: str
    options: dict[str, str]


class GameScorePayload(SQLModel):
    """One row of the live scoreboard."""

    player_id: str
    player_name: str
    score: int


class GameSessionStartedEvent(SQLModel):
    """Server event emitted after a session is created."""

    type: Literal["session_started"] = "session_started"
    session_id: str
    players: list[GamePlayerPayload]
    round_count: int
    round_seconds: int
    scoreboard: list[GameScorePayload]


class GameRoundStartedEvent(SQLModel):
    """Server event that starts a round and exposes the answer deadline."""

    type: Literal["round_started"] = "round_started"
    session_id: str
    round_number: int
    active_player: GamePlayerPayload
    question: GameQuestionPayload
    deadline_at: datetime
    scoreboard: list[GameScorePayload]
    comment_id: str | None = None
    comment_key: str | None = None


class GameAnswerResultEvent(SQLModel):
    """Server event with the judged answer and updated scoreboard."""

    type: Literal["answer_result"] = "answer_result"
    session_id: str
    round_number: int
    player: GamePlayerPayload
    question_id: str
    input_method: GameInputMethod
    submitted_answer: str
    matched_answer: AnswerLetter | None = None
    is_correct: bool
    correct_answer: AnswerLetter
    explanation: str | None = None
    score_delta: int = Field(ge=0)
    timed_out: bool = False
    scoreboard: list[GameScorePayload]
    comment_id: str | None = None
    comment_key: str | None = None


class GameSessionFinishedEvent(SQLModel):
    """Server event emitted when the final round is resolved."""

    type: Literal["session_finished"] = "session_finished"
    session_id: str
    scoreboard: list[GameScorePayload]
    winners: list[GameScorePayload]
    comment_id: str | None = None
    comment_key: str | None = None


class GameErrorEvent(SQLModel):
    """Server event used for protocol and validation failures."""

    type: Literal["error"] = "error"
    code: str
    message: str


GameClientMessage: TypeAlias = GameStartSessionMessage | GameSubmitAnswerMessage
GameServerEvent: TypeAlias = (
    GameSessionStartedEvent
    | GameRoundStartedEvent
    | GameAnswerResultEvent
    | GameSessionFinishedEvent
    | GameErrorEvent
)
