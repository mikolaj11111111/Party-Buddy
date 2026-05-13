import json
from pathlib import Path

from pydantic import ValidationError

from backend.app.models.question import Question


class QuestionLoaderError(ValueError):
    pass


def load_questions_from_directory(directory: Path) -> list[Question]:
    if not directory.exists():
        raise QuestionLoaderError(f"questions directory does not exist: {directory}")

    if not directory.is_dir():
        raise QuestionLoaderError(f"questions path is not a directory: {directory}")

    questions: list[Question] = []
    seen_ids: set[str] = set()

    for file_path in sorted(directory.glob("*.json")):
        loaded_questions = _load_questions_file(file_path)

        for question in loaded_questions:
            if question.id in seen_ids:
                raise QuestionLoaderError(f"duplicate question id: {question.id}")

            seen_ids.add(question.id)
            questions.append(question)

    if not questions:
        raise QuestionLoaderError(f"no question files found in: {directory}")

    return questions


def _load_questions_file(file_path: Path) -> list[Question]:
    try:
        raw_questions = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise QuestionLoaderError(f"invalid JSON in {file_path}: {error}") from error

    if not isinstance(raw_questions, list):
        raise QuestionLoaderError(f"questions file must contain a list: {file_path}")

    questions: list[Question] = []
    for index, raw_question in enumerate(raw_questions):
        try:
            questions.append(Question.model_validate(raw_question))
        except ValidationError as error:
            raise QuestionLoaderError(
                f"invalid question at {file_path}:{index}: {error}"
            ) from error

    return questions
