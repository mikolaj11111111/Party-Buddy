import pytest

from backend.app.core.game_engine import GameEngineError, create_game_session
from backend.app.models.question import Question


def make_question(index: int, correct_answer: str = "A") -> Question:
    """Create a valid test question with a unique id."""

    return Question.model_validate(
        {
            "id": f"question_{index:03}",
            "category": "general",
            "difficulty": "easy",
            "question": f"Question {index}?",
            "options": {
                "A": f"Correct {index}",
                "B": f"Wrong B {index}",
                "C": f"Wrong C {index}",
                "D": f"Wrong D {index}",
            },
            "correct_answer": correct_answer,
            "explanation": f"Explanation {index}",
            "aliases": {"A": [f"Alias {index}"]},
        }
    )


def make_questions(count: int) -> list[Question]:
    """Create enough valid questions for game-engine tests."""

    return [make_question(index) for index in range(1, count + 1)]


def test_create_game_session_initializes_queue_players_and_scores() -> None:
    session = create_game_session(
        player_names=["Ala", " Bartek "],
        questions=make_questions(12),
        session_id="session_1",
    )

    assert session.session_id == "session_1"
    assert session.round_count == 10
    assert session.round_seconds == 15
    assert session.current_round_number == 1
    assert session.current_question is not None
    assert session.current_question.id == "question_001"
    assert session.current_player is not None
    assert session.current_player.name == "Ala"
    assert session.scores == {"player_1": 0, "player_2": 0}
    assert session.remaining_questions == 10
    assert session.status == "in_progress"


def test_create_game_session_rejects_invalid_player_count() -> None:
    questions = make_questions(10)

    with pytest.raises(GameEngineError, match="1 to 6 players"):
        create_game_session(player_names=[], questions=questions)

    with pytest.raises(GameEngineError, match="1 to 6 players"):
        create_game_session(
            player_names=[str(index) for index in range(7)], questions=questions
        )


def test_create_game_session_rejects_empty_player_name() -> None:
    with pytest.raises(GameEngineError, match="player name"):
        create_game_session(player_names=["Ala", "  "], questions=make_questions(10))


def test_create_game_session_rejects_too_short_question_queue() -> None:
    with pytest.raises(GameEngineError, match="not enough questions"):
        create_game_session(player_names=["Ala"], questions=make_questions(9))


def test_submit_answer_scores_correct_answer_and_advances_turn() -> None:
    session = create_game_session(
        player_names=["Ala", "Bartek"],
        questions=make_questions(10),
    )

    record = session.submit_answer(answer_letter="A")

    assert record.round_number == 1
    assert record.player_id == "player_1"
    assert record.question_id == "question_001"
    assert record.is_correct is True
    assert record.score_delta == 1
    assert session.scores["player_1"] == 1
    assert session.current_question is not None
    assert session.current_question.id == "question_002"
    assert session.current_player is not None
    assert session.current_player.id == "player_2"
    assert session.remaining_questions == 9


def test_submit_answer_keeps_score_for_wrong_answer() -> None:
    session = create_game_session(
        player_names=["Ala"],
        questions=make_questions(10),
    )

    record = session.submit_answer(answer_letter="B")

    assert record.is_correct is False
    assert record.score_delta == 0
    assert session.scores["player_1"] == 0


def test_submit_answer_accepts_text_alias_through_judge() -> None:
    session = create_game_session(
        player_names=["Ala"],
        questions=make_questions(10),
    )

    record = session.submit_answer(answer_text="alias 1")

    assert record.is_correct is True
    assert record.matched_answer == "A"
    assert session.scores["player_1"] == 1


def test_hotseat_rotates_players_across_questions() -> None:
    session = create_game_session(
        player_names=["Ala", "Bartek", "Celina"],
        questions=make_questions(10),
    )

    player_ids: list[str] = []
    for _ in range(5):
        assert session.current_player is not None
        player_ids.append(session.current_player.id)
        session.submit_answer(answer_letter="A")

    assert player_ids == ["player_1", "player_2", "player_3", "player_1", "player_2"]


def test_session_finishes_after_last_round() -> None:
    session = create_game_session(
        player_names=["Ala"],
        questions=make_questions(10),
    )

    for _ in range(10):
        session.submit_answer(answer_letter="A")

    assert session.status == "finished"
    assert session.current_question is None
    assert session.current_player is None
    assert session.remaining_questions == 0
    assert session.scores["player_1"] == 10

    with pytest.raises(GameEngineError, match="already finished"):
        session.submit_answer(answer_letter="A")


def test_submit_timeout_records_wrong_answer_and_advances_turn() -> None:
    session = create_game_session(
        player_names=["Ala", "Bartek"],
        questions=make_questions(10),
    )

    record = session.submit_timeout()

    assert record.round_number == 1
    assert record.player_id == "player_1"
    assert record.question_id == "question_001"
    assert record.submitted_answer == "timeout"
    assert record.is_correct is False
    assert record.score_delta == 0
    assert session.scores["player_1"] == 0
    assert session.current_player is not None
    assert session.current_player.id == "player_2"
    assert session.current_question is not None
    assert session.current_question.id == "question_002"


def test_scoreboard_orders_by_score_and_keeps_turn_order_for_ties() -> None:
    session = create_game_session(
        player_names=["Ala", "Bartek", "Celina"],
        questions=make_questions(10),
    )

    session.submit_answer(answer_letter="A")
    session.submit_answer(answer_letter="B")
    session.submit_answer(answer_letter="A")

    scoreboard = session.get_scoreboard()

    assert [row.player_name for row in scoreboard] == ["Ala", "Celina", "Bartek"]
    assert [row.score for row in scoreboard] == [1, 1, 0]
