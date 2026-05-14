import pytest
from pydantic import ValidationError
from sqlalchemy import inspect
from sqlmodel import Session as DbSession
from sqlmodel import SQLModel, create_engine, select

from backend.app.models import Profile, Question, Score
from backend.app.models.session import Session as GameSession


def make_db_question() -> Question:
    """Create a valid persisted question model for DB tests."""

    return Question.model_validate(
        {
            "id": "db_question_001",
            "category": "general",
            "difficulty": "easy",
            "question": "Test question?",
            "options": {
                "A": "Correct",
                "B": "Wrong B",
                "C": "Wrong C",
                "D": "Wrong D",
            },
            "correct_answer": "A",
            "explanation": "Because A is correct.",
            "aliases": {"A": ["correct alias"]},
        }
    )


def test_domain_models_create_expected_tables() -> None:
    engine = create_engine("sqlite:///:memory:")

    SQLModel.metadata.create_all(engine)

    table_names = set(inspect(engine).get_table_names())
    assert {"questions", "profiles", "game_sessions", "scores"} <= table_names


def test_domain_models_roundtrip_through_sqlite() -> None:
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    profile = Profile(id="global", display_name="Player")
    question = make_db_question()
    game_session = GameSession(
        id="session_001",
        profile_id=profile.id,
        mode="hotseat",
        total_rounds=10,
        round_seconds=15,
    )
    score = Score(
        session_id=game_session.id,
        player_id="player_1",
        player_name="Ala",
        player_order=0,
        score=3,
        correct_answers=3,
        answered_questions=5,
    )

    with DbSession(engine) as db_session:
        db_session.add(profile)
        db_session.add(question)
        db_session.add(game_session)
        db_session.add(score)
        db_session.commit()

    with DbSession(engine) as db_session:
        stored_question = db_session.exec(select(Question)).one()
        stored_profile = db_session.exec(select(Profile)).one()
        stored_session = db_session.exec(select(GameSession)).one()
        stored_score = db_session.exec(select(Score)).one()

    assert stored_question.options["A"] == "Correct"
    assert stored_question.aliases["A"] == ["correct alias"]
    assert stored_question.correct_answer == "A"
    assert stored_profile.display_name == "Player"
    assert stored_session.mode == "hotseat"
    assert stored_score.player_name == "Ala"
    assert stored_score.score == 3


def test_profile_rejects_empty_display_name() -> None:
    with pytest.raises(ValidationError):
        Profile.model_validate({"id": "global", "display_name": "   "})


def test_session_rejects_current_round_after_total_rounds() -> None:
    with pytest.raises(ValidationError):
        GameSession.model_validate(
            {
                "id": "session_001",
                "profile_id": "global",
                "total_rounds": 10,
                "current_round": 11,
            }
        )


def test_score_rejects_empty_player_name() -> None:
    with pytest.raises(ValidationError):
        Score.model_validate(
            {
                "session_id": "session_001",
                "player_id": "player_1",
                "player_name": " ",
                "player_order": 0,
            }
        )
