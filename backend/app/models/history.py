from datetime import datetime

from sqlmodel import SQLModel

from backend.app.models.session import SessionMode


class GameHistoryScore(SQLModel):
    """One player row in a stored session summary."""

    player_id: str
    player_name: str
    player_order: int
    score: int
    correct_answers: int
    answered_questions: int


class GameHistorySession(SQLModel):
    """Public summary of one finished local trivia session."""

    id: str
    mode: SessionMode
    total_rounds: int
    round_seconds: int
    created_at: datetime
    finished_at: datetime | None
    top_score: int
    winners: list[str]
    players: list[GameHistoryScore]
