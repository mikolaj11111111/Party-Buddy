import pytest

from backend.app.core.judge import (
    judge_answer,
    normalize_answer_text,
    parse_answer_letter,
)
from backend.app.models.question import Question


@pytest.fixture
def make_question() -> Question:
    return Question(
        id="geo_test_001",
        category="geography",
        difficulty="easy",
        question="Jaka jest stolica Polski?",
        options={
            "A": "Krak\u00f3w",
            "B": "Warszawa",
            "C": "Gda\u0144sk",
            "D": "Wroc\u0142aw",
        },
        correct_answer="B",
        explanation="Stolic\u0105 Polski jest Warszawa.",
        aliases={
            "B": ["wawa", "warsaw", "warszawka"],
        },
    )


def test_correct_letter_answer_is_accepted(make_question: Question) -> None:
    result = judge_answer(make_question, answer_letter="b")

    assert result.is_correct
    assert result.matched_answer == "B"
    assert result.match_type == "letter"
    assert result.score_delta == 1


def test_wrong_letter_answer_is_rejected(make_question: Question) -> None:
    result = judge_answer(make_question, answer_letter="A")

    assert not result.is_correct
    assert result.matched_answer == "A"
    assert result.match_type == "letter"
    assert result.score_delta == 0


def test_correct_text_answer_is_case_insensitive(make_question: Question) -> None:
    result = judge_answer(make_question, answer_text="WARSZAWA")

    assert result.is_correct
    assert result.matched_answer == "B"
    assert result.match_type == "option_text"


def test_alias_answer_is_accepted(make_question: Question) -> None:
    result = judge_answer(make_question, answer_text="wawa")

    assert result.is_correct
    assert result.matched_answer == "B"
    assert result.match_type == "alias"


def test_typo_answer_is_accepted_by_fuzzy_matching(make_question: Question) -> None:
    result = judge_answer(make_question, answer_text="warszawaa")

    assert result.is_correct
    assert result.matched_answer == "B"
    assert result.match_type == "fuzzy"


def test_wrong_text_answer_is_rejected(make_question: Question) -> None:
    result = judge_answer(make_question, answer_text="Krakow")

    assert not result.is_correct
    assert result.matched_answer == "A"
    assert result.match_type == "option_text"
    assert result.score_delta == 0


def test_answer_letter_has_priority_over_conflicting_text(
    make_question: Question,
) -> None:
    result = judge_answer(
        make_question,
        answer_letter="A",
        answer_text="Warszawa",
    )

    assert not result.is_correct
    assert result.matched_answer == "A"
    assert result.match_type == "letter"


def test_missing_answer_raises_error(make_question: Question) -> None:
    with pytest.raises(ValueError):
        judge_answer(make_question)


def test_polish_diacritics_are_normalized() -> None:
    assert normalize_answer_text("\u0141\u00f3d\u017a") == "lodz"
    assert normalize_answer_text("Wroc\u0142aw") == "wroclaw"


def test_voice_letter_phrases_are_parsed() -> None:
    assert parse_answer_letter("odpowied\u017a be") == "B"
    assert parse_answer_letter("opcja C") == "C"
