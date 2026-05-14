from collections import Counter
from pathlib import Path

from backend.app.core.question_loader import load_questions_from_directory

QUESTIONS_DIR = Path("data/questions")
EXPECTED_CATEGORIES = {
    "geography",
    "history",
    "popculture",
    "movies",
    "music",
    "science",
    "internet_games",
    "sport",
    "technology",
    "language_literature",
    "general",
}
MIN_TOTAL_QUESTIONS = 180
MAX_TOTAL_QUESTIONS = 181
MIN_CATEGORY_QUESTIONS = 16
MAX_CATEGORY_QUESTIONS = 17


def test_questions_dataset_has_full_m2_batch() -> None:
    questions = load_questions_from_directory(QUESTIONS_DIR)

    category_counts = Counter(question.category for question in questions)

    assert MIN_TOTAL_QUESTIONS <= len(questions) <= MAX_TOTAL_QUESTIONS
    assert set(category_counts) == EXPECTED_CATEGORIES
    assert all(
        MIN_CATEGORY_QUESTIONS <= count <= MAX_CATEGORY_QUESTIONS
        for count in category_counts.values()
    )


def test_questions_dataset_has_balanced_correct_answers_per_category() -> None:
    questions = load_questions_from_directory(QUESTIONS_DIR)

    for category in EXPECTED_CATEGORIES:
        answers = Counter(
            question.correct_answer
            for question in questions
            if question.category == category
        )

        assert set(answers) == {"A", "B", "C", "D"}
        assert max(answers.values()) <= 6


def test_questions_dataset_has_no_lost_polish_character_markers() -> None:
    questions = load_questions_from_directory(QUESTIONS_DIR)

    broken_fields: list[str] = []
    for question in questions:
        checked_question_text = question.question.rstrip()
        if checked_question_text.endswith("?"):
            checked_question_text = checked_question_text[:-1]

        if "?" in checked_question_text:
            broken_fields.append(f"{question.id}.question")

        for letter, option in question.options.items():
            if "?" in option:
                broken_fields.append(f"{question.id}.options.{letter}")

        if question.explanation and "?" in question.explanation:
            broken_fields.append(f"{question.id}.explanation")

        if question.aliases:
            for letter, aliases in question.aliases.items():
                for alias in aliases:
                    if "?" in alias:
                        broken_fields.append(f"{question.id}.aliases.{letter}")

    assert broken_fields == []


def test_questions_dataset_questions_end_with_question_mark() -> None:
    questions = load_questions_from_directory(QUESTIONS_DIR)

    invalid_question_ids = [
        question.id
        for question in questions
        if not question.question.rstrip().endswith("?")
    ]

    assert invalid_question_ids == []


def test_questions_dataset_has_sources_file() -> None:
    sources_path = QUESTIONS_DIR / "SOURCES.md"

    assert sources_path.exists()
    assert "Open Trivia Database" in sources_path.read_text(encoding="utf-8")
