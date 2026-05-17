import json
from collections import Counter
from pathlib import Path
from typing import Any

DATASET_DIR = Path("data/5_seconds")
PROMPTS_PATH = DATASET_DIR / "prompts.json"
EXPECTED_CATEGORIES = {
    "everyday",
    "food",
    "geography",
    "sport",
    "popculture",
    "internet_games",
    "technology",
    "language",
    "school_work",
    "travel",
    "home",
    "party",
}
EXPECTED_DIFFICULTIES = {"easy", "medium", "hard"}
EXPECTED_TOTAL_PROMPTS = 120
EXPECTED_PROMPTS_PER_CATEGORY = 10
EXPECTED_ANSWER_COUNT = 3


def load_prompts() -> list[dict[str, Any]]:
    """Load the authored 5 Seconds prompt dataset."""

    return json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))


def test_five_seconds_dataset_has_expected_size_and_categories() -> None:
    prompts = load_prompts()

    category_counts = Counter(prompt["category"] for prompt in prompts)

    assert len(prompts) == EXPECTED_TOTAL_PROMPTS
    assert set(category_counts) == EXPECTED_CATEGORIES
    assert all(
        count == EXPECTED_PROMPTS_PER_CATEGORY for count in category_counts.values()
    )


def test_five_seconds_dataset_has_valid_prompt_schema() -> None:
    prompts = load_prompts()

    invalid_prompt_ids: list[str] = []
    for prompt in prompts:
        prompt_id = prompt.get("id", "")
        sample_answers = prompt.get("sample_answers", [])

        if set(prompt) != {
            "id",
            "category",
            "difficulty",
            "prompt",
            "expected_answer_count",
            "sample_answers",
        }:
            invalid_prompt_ids.append(prompt_id)
            continue

        if not isinstance(prompt_id, str) or not prompt_id.startswith("fs_"):
            invalid_prompt_ids.append(prompt_id)

        if prompt["category"] not in EXPECTED_CATEGORIES:
            invalid_prompt_ids.append(prompt_id)

        if prompt["difficulty"] not in EXPECTED_DIFFICULTIES:
            invalid_prompt_ids.append(prompt_id)

        if not isinstance(prompt["prompt"], str) or not prompt["prompt"].startswith(
            "Wymień 3 "
        ):
            invalid_prompt_ids.append(prompt_id)

        if prompt["expected_answer_count"] != EXPECTED_ANSWER_COUNT:
            invalid_prompt_ids.append(prompt_id)

        if (
            not isinstance(sample_answers, list)
            or len(sample_answers) < EXPECTED_ANSWER_COUNT
            or any(
                not isinstance(answer, str) or not answer for answer in sample_answers
            )
            or len(sample_answers) != len(set(sample_answers))
        ):
            invalid_prompt_ids.append(prompt_id)

    assert invalid_prompt_ids == []


def test_five_seconds_dataset_has_unique_ids_and_prompts() -> None:
    prompts = load_prompts()

    ids = [prompt["id"] for prompt in prompts]
    prompt_texts = [prompt["prompt"].casefold() for prompt in prompts]

    assert len(ids) == len(set(ids))
    assert len(prompt_texts) == len(set(prompt_texts))


def test_five_seconds_dataset_has_clean_text_encoding() -> None:
    prompts = load_prompts()

    broken_fields: list[str] = []
    for prompt in prompts:
        checked_fields = [
            ("prompt", prompt["prompt"]),
            *[
                (f"sample_answers.{index}", sample_answer)
                for index, sample_answer in enumerate(prompt["sample_answers"])
            ],
        ]

        for field_name, value in checked_fields:
            if "?" in value:
                broken_fields.append(f"{prompt['id']}.{field_name}")

            if any("\u0400" <= character <= "\u04ff" for character in value):
                broken_fields.append(f"{prompt['id']}.{field_name}")

    assert broken_fields == []


def test_five_seconds_dataset_has_sources_file() -> None:
    sources_path = DATASET_DIR / "SOURCES.md"

    assert sources_path.exists()
    assert "locally authored" in sources_path.read_text(encoding="utf-8")
