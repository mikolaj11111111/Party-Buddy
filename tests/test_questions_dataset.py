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


def test_questions_dataset_has_sources_file() -> None:
    sources_path = QUESTIONS_DIR / "SOURCES.md"

    assert sources_path.exists()
    assert "Open Trivia Database" in sources_path.read_text(encoding="utf-8")
