from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.core.question_loader import load_questions_from_directory
from backend.app.main import app


def test_answer_endpoint_accepts_correct_letter() -> None:
    question = load_questions_from_directory(Path("data/trivia/questions"))[0]

    with TestClient(app) as client:
        response = client.post(
            "/api/answer",
            json={
                "question_id": question.id,
                "input_method": "click",
                "answer_letter": question.correct_answer,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["question_id"] == question.id
    assert body["is_correct"] is True
    assert body["matched_answer"] == question.correct_answer
    assert body["correct_answer"] == question.correct_answer
    assert body["score_delta"] == 1


def test_answer_endpoint_accepts_correct_text() -> None:
    question = load_questions_from_directory(Path("data/trivia/questions"))[0]
    answer_text = question.options[question.correct_answer]

    with TestClient(app) as client:
        response = client.post(
            "/api/answer",
            json={
                "question_id": question.id,
                "input_method": "voice",
                "answer_text": answer_text,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["is_correct"] is True
    assert body["matched_answer"] == question.correct_answer


def test_answer_endpoint_returns_404_for_unknown_question() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/answer",
            json={
                "question_id": "missing_question",
                "input_method": "click",
                "answer_letter": "A",
            },
        )

    assert response.status_code == 404


def test_answer_endpoint_returns_422_for_missing_answer() -> None:
    question = load_questions_from_directory(Path("data/trivia/questions"))[0]

    with TestClient(app) as client:
        response = client.post(
            "/api/answer",
            json={
                "question_id": question.id,
                "input_method": "click",
            },
        )

    assert response.status_code == 422
