import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

DATASET_DIR = Path("data/hangman")
WORDS_PATH = DATASET_DIR / "words.json"
EXPECTED_CATEGORIES = {
    "abstract",
    "animals",
    "cities",
    "countries",
    "food",
    "jobs",
    "names",
    "nature",
    "objects",
    "plants",
    "popculture",
    "sports",
    "technology",
}
EXPECTED_DIFFICULTIES = {"easy", "medium", "hard"}
EXPECTED_TOTAL_WORDS = 195
EXPECTED_WORDS_PER_CATEGORY = 15
WORD_PATTERN = re.compile(r"^[a-ząćęłńóśźż ]+$")


def load_words() -> list[dict[str, Any]]:
    """Load the authored Hangman word dataset."""

    return json.loads(WORDS_PATH.read_text(encoding="utf-8"))


def test_hangman_dataset_has_expected_size_and_categories() -> None:
    words = load_words()

    category_counts = Counter(word["category"] for word in words)

    assert len(words) == EXPECTED_TOTAL_WORDS
    assert set(category_counts) == EXPECTED_CATEGORIES
    assert all(
        count == EXPECTED_WORDS_PER_CATEGORY for count in category_counts.values()
    )


def test_hangman_dataset_has_valid_schema() -> None:
    words = load_words()

    invalid_word_ids: list[str] = []
    for word in words:
        word_id = word.get("id", "")
        if set(word) != {"id", "category", "difficulty", "word", "hint"}:
            invalid_word_ids.append(word_id)
            continue

        if not isinstance(word_id, str) or not word_id.startswith("hangman_"):
            invalid_word_ids.append(word_id)

        if word["category"] not in EXPECTED_CATEGORIES:
            invalid_word_ids.append(word_id)

        if word["difficulty"] not in EXPECTED_DIFFICULTIES:
            invalid_word_ids.append(word_id)

        if not isinstance(word["word"], str) or not WORD_PATTERN.fullmatch(
            word["word"]
        ):
            invalid_word_ids.append(word_id)

        if len(word["word"].replace(" ", "")) < 3:
            invalid_word_ids.append(word_id)

        if not isinstance(word["hint"], str) or not word["hint"].strip():
            invalid_word_ids.append(word_id)

    assert invalid_word_ids == []


def test_hangman_dataset_has_unique_ids_and_words() -> None:
    words = load_words()

    ids = [word["id"] for word in words]
    normalized_words = [word["word"].casefold() for word in words]

    assert len(ids) == len(set(ids))
    assert len(normalized_words) == len(set(normalized_words))


def test_hangman_dataset_has_clean_text_encoding() -> None:
    words = load_words()

    broken_fields: list[str] = []
    for word in words:
        checked_fields = [
            ("word", word["word"]),
            ("hint", word["hint"]),
        ]

        for field_name, value in checked_fields:
            if "?" in value:
                broken_fields.append(f"{word['id']}.{field_name}")

            if any("\u0400" <= character <= "\u04ff" for character in value):
                broken_fields.append(f"{word['id']}.{field_name}")

    assert broken_fields == []


def test_hangman_dataset_has_sources_file() -> None:
    sources_path = DATASET_DIR / "SOURCES.md"

    assert sources_path.exists()
    assert "locally authored" in sources_path.read_text(encoding="utf-8")
