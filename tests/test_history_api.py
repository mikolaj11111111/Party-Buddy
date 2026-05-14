from collections.abc import Generator
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session as DbSession
from sqlmodel import SQLModel, create_engine

from backend.app.core.game_engine import create_game_session
from backend.app.core.game_history import save_finished_game_session
from backend.app.db import get_session
from backend.app.main import app
from backend.app.models.question import Question


def make_question() -> Question:
    """Create a valid question for history endpoint tests."""

    return Question.model_validate(
        {
            "id": "history_api_question_001",
            "category": "general",
            "difficulty": "easy",
            "question": "Endpoint history question?",
            "options": {
                "A": "Correct",
                "B": "Wrong B",
                "C": "Wrong C",
                "D": "Wrong D",
            },
            "correct_answer": "A",
            "explanation": "Because A is correct.",
            "aliases": {"A": ["correct"]},
        }
    )


def test_history_endpoint_returns_finished_sessions() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    game_session = create_game_session(
        session_id="history_api_session_001",
        player_names=["Ala"],
        questions=[make_question()],
        round_count=1,
    )
    game_session.submit_answer(answer_letter="A")
    started_at = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)

    with DbSession(engine) as db_session:
        save_finished_game_session(
            db_session,
            game_session,
            started_at=started_at,
            finished_at=started_at + timedelta(minutes=1),
        )

    def override_get_session() -> Generator[DbSession]:
        with DbSession(engine) as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(app) as client:
            response = client.get("/api/history/sessions")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "history_api_session_001",
            "mode": "solo",
            "total_rounds": 1,
            "round_seconds": 15,
            "created_at": "2026-01-01T12:00:00",
            "finished_at": "2026-01-01T12:01:00",
            "top_score": 1,
            "winners": ["Ala"],
            "players": [
                {
                    "player_id": "player_1",
                    "player_name": "Ala",
                    "player_order": 0,
                    "score": 1,
                    "correct_answers": 1,
                    "answered_questions": 1,
                }
            ],
        }
    ]
