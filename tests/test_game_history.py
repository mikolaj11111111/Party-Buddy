from datetime import UTC, datetime, timedelta

from sqlalchemy.pool import StaticPool
from sqlmodel import Session as DbSession
from sqlmodel import SQLModel, create_engine, select

from backend.app.core.game_engine import create_game_session
from backend.app.core.game_history import (
    list_finished_game_sessions,
    save_finished_game_session,
)
from backend.app.models.question import Question
from backend.app.models.score import Score
from backend.app.models.session import Session as StoredSession
from backend.app.models.session import SessionMode, SessionStatus


def make_history_engine():
    """Create an in-memory SQLite engine shared across DB sessions."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def make_question(index: int, correct_answer: str = "A") -> Question:
    """Create a valid question for history persistence tests."""

    return Question.model_validate(
        {
            "id": f"history_question_{index:03}",
            "category": "general",
            "difficulty": "easy",
            "question": f"History question {index}?",
            "options": {
                "A": f"Correct A {index}",
                "B": f"Correct B {index}",
                "C": f"Wrong C {index}",
                "D": f"Wrong D {index}",
            },
            "correct_answer": correct_answer,
            "explanation": f"Explanation {index}",
            "aliases": {correct_answer: [f"Alias {index}"]},
        }
    )


def make_finished_session():
    """Create a completed two-player session with one winner."""

    game_session = create_game_session(
        session_id="history_session_001",
        player_names=["Ala", "Bartek"],
        questions=[make_question(1, "A"), make_question(2, "B")],
        round_count=2,
        round_seconds=15,
    )
    game_session.submit_answer(answer_letter="A")
    game_session.submit_answer(answer_letter="C")
    return game_session


def test_save_finished_game_session_persists_summary_and_scores() -> None:
    engine = make_history_engine()
    started_at = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    finished_at = started_at + timedelta(minutes=2)

    with DbSession(engine) as db_session:
        summary = save_finished_game_session(
            db_session,
            make_finished_session(),
            started_at=started_at,
            finished_at=finished_at,
        )

        stored_session = db_session.exec(select(StoredSession)).one()
        score_rows = db_session.exec(select(Score)).all()

    assert summary.id == "history_session_001"
    assert summary.mode == SessionMode.hotseat
    assert summary.top_score == 1
    assert summary.winners == ["Ala"]
    assert stored_session.status == SessionStatus.finished
    assert stored_session.total_rounds == 2
    assert len(score_rows) == 2
    assert [(score.player_name, score.score) for score in summary.players] == [
        ("Ala", 1),
        ("Bartek", 0),
    ]
    assert summary.players[0].correct_answers == 1
    assert summary.players[0].answered_questions == 1


def test_save_finished_game_session_is_idempotent() -> None:
    engine = make_history_engine()
    started_at = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    finished_at = started_at + timedelta(minutes=2)

    with DbSession(engine) as db_session:
        game_session = make_finished_session()
        first_summary = save_finished_game_session(
            db_session,
            game_session,
            started_at=started_at,
            finished_at=finished_at,
        )
        second_summary = save_finished_game_session(
            db_session,
            game_session,
            started_at=started_at,
            finished_at=finished_at,
        )

        score_rows = db_session.exec(select(Score)).all()

    assert first_summary.id == second_summary.id
    assert len(score_rows) == 2


def test_list_finished_game_sessions_orders_newest_first() -> None:
    engine = make_history_engine()
    first_start = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    second_start = datetime(2026, 1, 2, 12, 0, tzinfo=UTC)

    first_session = make_finished_session()
    second_session = make_finished_session()
    second_session.session_id = "history_session_002"

    with DbSession(engine) as db_session:
        save_finished_game_session(
            db_session,
            first_session,
            started_at=first_start,
            finished_at=first_start + timedelta(minutes=1),
        )
        save_finished_game_session(
            db_session,
            second_session,
            started_at=second_start,
            finished_at=second_start + timedelta(minutes=1),
        )

        summaries = list_finished_game_sessions(db_session)

    assert [summary.id for summary in summaries] == [
        "history_session_002",
        "history_session_001",
    ]
