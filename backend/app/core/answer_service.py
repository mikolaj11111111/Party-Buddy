from dataclasses import asdict
from pathlib import Path

from backend.app.core.judge import judge_answer
from backend.app.core.question_loader import load_questions_from_directory
from backend.app.db import PROJECT_ROOT
from backend.app.models.answer import AnswerRequest, AnswerResponse

QUESTIONS_DIRECTORY = PROJECT_ROOT / "data" / "questions"


class AnswerServiceError(ValueError):
    pass


class QuestionNotFoundError(AnswerServiceError):
    pass


def answer_question(
    answer_request: AnswerRequest,
    questions_directory: Path = QUESTIONS_DIRECTORY,
) -> AnswerResponse:
    questions = load_questions_from_directory(questions_directory)
    question = next(
        (
            candidate
            for candidate in questions
            if candidate.id == answer_request.question_id
        ),
        None,
    )

    if question is None:
        raise QuestionNotFoundError(f"question not found: {answer_request.question_id}")

    judge_result = judge_answer(
        question,
        answer_letter=answer_request.answer_letter,
        answer_text=answer_request.answer_text,
    )

    return AnswerResponse.model_validate(asdict(judge_result))
