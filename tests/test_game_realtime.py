from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from backend.app.core.game_realtime import GameProtocolError, GameSessionController
from backend.app.main import app
from backend.app.models.question import Question


class FakeClock:
    """Mutable UTC clock for deterministic realtime-controller tests."""

    def __init__(self) -> None:
        """Start all tests from a fixed point in time."""

        self.current = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)

    def now(self) -> datetime:
        """Return the current fake timestamp."""

        return self.current

    def advance(self, seconds: int) -> None:
        """Move the fake timestamp forward."""

        self.current += timedelta(seconds=seconds)


def make_question(index: int, correct_answer: str = "A") -> Question:
    """Create a valid question for realtime tests."""

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
    """Create a stable question pool."""

    return [make_question(index) for index in range(1, count + 1)]


def test_controller_starts_session_and_hides_correct_answer() -> None:
    clock = FakeClock()
    controller = GameSessionController(
        make_questions(2),
        now=clock.now,
        shuffle_questions=False,
    )

    events = controller.handle_payload(
        {
            "type": "start_session",
            "players": ["Ala", "Bartek"],
            "round_count": 2,
            "round_seconds": 15,
        }
    )

    assert [event.type for event in events] == ["session_started", "round_transition"]
    transition = events[1].model_dump(mode="json")
    assert transition["phase"] == "intro"
    assert transition["next_active_player"]["player_name"] == "Ala"
    assert transition["next_round_number"] == 1
    assert transition["starts_at"] == "2026-01-01T12:00:03Z"
    assert transition["transition_seconds"] == 3
    assert transition["comment_id"] == "intro_001"
    assert len(transition["comment_key"]) == 64

    clock.advance(3)
    round_started = controller.start_next_round_after_transition().model_dump(
        mode="json"
    )
    assert round_started["active_player"]["player_name"] == "Ala"
    assert round_started["question"]["id"] == "question_001"
    assert "correct_answer" not in round_started["question"]
    assert round_started["deadline_at"] == "2026-01-01T12:00:18Z"


def test_controller_submits_answer_and_schedules_next_round_transition() -> None:
    clock = FakeClock()
    controller = GameSessionController(
        make_questions(2),
        now=clock.now,
        shuffle_questions=False,
    )
    controller.handle_payload(
        {
            "type": "start_session",
            "players": ["Ala", "Bartek"],
            "round_count": 2,
        }
    )
    clock.advance(3)
    controller.start_next_round_after_transition()

    events = controller.handle_payload(
        {
            "type": "submit_answer",
            "question_id": "question_001",
            "input_method": "click",
            "answer_letter": "A",
        }
    )

    assert [event.type for event in events] == ["answer_result", "round_transition"]
    answer_result = events[0].model_dump(mode="json")
    transition = events[1].model_dump(mode="json")
    assert answer_result["is_correct"] is True
    assert answer_result["score_delta"] == 1
    assert answer_result["scoreboard"][0]["player_name"] == "Ala"
    assert answer_result["comment_id"] == "correct_001"
    assert transition["phase"] == "between_rounds"
    assert transition["next_active_player"]["player_name"] == "Bartek"
    assert transition["next_round_number"] == 2
    assert transition["starts_at"] == "2026-01-01T12:00:06Z"

    clock.advance(3)
    round_started = controller.start_next_round_after_transition().model_dump(
        mode="json"
    )
    assert round_started["active_player"]["player_name"] == "Bartek"
    assert round_started["question"]["id"] == "question_002"
    assert round_started["deadline_at"] == "2026-01-01T12:00:21Z"


def test_controller_resolves_timeout_and_finishes_session() -> None:
    clock = FakeClock()
    controller = GameSessionController(
        make_questions(1),
        now=clock.now,
        shuffle_questions=False,
    )
    controller.handle_payload(
        {
            "type": "start_session",
            "players": ["Ala"],
            "round_count": 1,
            "round_seconds": 1,
        }
    )
    clock.advance(3)
    controller.start_next_round_after_transition()

    clock.advance(2)
    events = controller.handle_round_timeout()

    assert [event.type for event in events] == ["answer_result", "session_ending"]
    answer_result = events[0].model_dump(mode="json")
    ending = events[1].model_dump(mode="json")
    assert answer_result["timed_out"] is True
    assert answer_result["input_method"] == "timeout"
    assert answer_result["is_correct"] is False
    assert answer_result["comment_key"] is None
    assert ending["ends_at"] == "2026-01-01T12:00:08Z"
    assert ending["ending_seconds"] == 3
    assert ending["comment_id"] == "outro_001"
    assert len(ending["comment_key"]) == 64

    clock.advance(3)
    finished = controller.finish_session_after_ending().model_dump(mode="json")
    assert finished["winners"] == [
        {"player_id": "player_1", "player_name": "Ala", "score": 0}
    ]
    assert finished["comment_id"] is None


def test_controller_rejects_answer_before_session_start() -> None:
    controller = GameSessionController(make_questions(1), shuffle_questions=False)

    with pytest.raises(GameProtocolError, match="has not started"):
        controller.handle_payload(
            {
                "type": "submit_answer",
                "question_id": "question_001",
                "input_method": "click",
                "answer_letter": "A",
            }
        )


def test_game_websocket_runs_one_round() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/ws/game") as websocket:
            websocket.send_json(
                {
                    "type": "start_session",
                    "players": ["Ala"],
                    "categories": ["geography"],
                    "round_count": 1,
                    "round_seconds": 30,
                }
            )

            session_started = websocket.receive_json()
            intro = websocket.receive_json()

    assert session_started["type"] == "session_started"
    assert intro["type"] == "round_transition"
    assert intro["phase"] == "intro"
    assert intro["transition_seconds"] == 3
