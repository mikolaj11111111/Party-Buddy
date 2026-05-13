import pytest
from pydantic import ValidationError

from backend.app.models.answer import AnswerRequest, AnswerResponse


def test_answer_request_accepts_click_letter() -> None:
    request = AnswerRequest.model_validate(
        {
            "question_id": "geo_001",
            "input_method": "click",
            "answer_letter": " b ",
        }
    )

    assert request.question_id == "geo_001"
    assert request.input_method == "click"
    assert request.answer_letter == "B"
    assert request.answer_text is None


def test_answer_request_accepts_voice_text() -> None:
    request = AnswerRequest.model_validate(
        {
            "question_id": "geo_001",
            "input_method": "voice",
            "answer_text": " Warszawa ",
        }
    )

    assert request.answer_letter is None
    assert request.answer_text == "Warszawa"


def test_answer_request_accepts_text_input() -> None:
    request = AnswerRequest.model_validate(
        {
            "question_id": "geo_001",
            "input_method": "text",
            "answer_text": "wawa",
        }
    )

    assert request.input_method == "text"
    assert request.answer_text == "wawa"


def test_answer_request_rejects_missing_answer() -> None:
    with pytest.raises(ValidationError):
        AnswerRequest.model_validate(
            {
                "question_id": "geo_001",
                "input_method": "click",
            }
        )


def test_answer_request_rejects_invalid_input_method() -> None:
    with pytest.raises(ValidationError):
        AnswerRequest.model_validate(
            {
                "question_id": "geo_001",
                "input_method": "keyboard",
                "answer_text": "Warszawa",
            }
        )


def test_answer_request_rejects_invalid_letter() -> None:
    with pytest.raises(ValidationError):
        AnswerRequest.model_validate(
            {
                "question_id": "geo_001",
                "input_method": "click",
                "answer_letter": "E",
            }
        )


def test_answer_response_accepts_judge_result_shape() -> None:
    response = AnswerResponse.model_validate(
        {
            "question_id": "geo_001",
            "submitted_answer": "Warszawa",
            "matched_answer": "B",
            "is_correct": True,
            "correct_answer": "B",
            "explanation": "Stolicą Polski jest Warszawa.",
            "score_delta": 1,
        }
    )

    assert response.is_correct
    assert response.matched_answer == "B"
    assert response.score_delta == 1


def test_answer_response_rejects_negative_score_delta() -> None:
    with pytest.raises(ValidationError):
        AnswerResponse.model_validate(
            {
                "question_id": "geo_001",
                "submitted_answer": "Warszawa",
                "matched_answer": "B",
                "is_correct": True,
                "correct_answer": "B",
                "score_delta": -1,
            }
        )
