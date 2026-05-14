import re
import unicodedata
from dataclasses import dataclass
from typing import Literal, cast

from rapidfuzz import fuzz

from backend.app.models.question import AnswerLetter, Question

MatchType = Literal["letter", "option_text", "alias", "fuzzy", "none"]

FUZZY_MATCH_THRESHOLD = 85.0
LETTER_WORDS: dict[str, AnswerLetter] = {
    "a": "A",
    "b": "B",
    "be": "B",
    "c": "C",
    "ce": "C",
    "d": "D",
    "de": "D",
}
LETTER_FILLER_WORDS = {
    "litera",
    "odpowied",
    "odpowiedz",
    "odpowiedzi",
    "opcja",
    "to",
    "wariant",
    "wybieram",
}
POLISH_CHARACTER_TRANSLATION = str.maketrans(
    {
        "ł": "l",
        "Ł": "L",
    }
)


@dataclass(frozen=True)
class JudgeResult:
    """Final answer evaluation returned by the deterministic judge."""

    question_id: str
    submitted_answer: str
    matched_answer: AnswerLetter | None
    is_correct: bool
    correct_answer: AnswerLetter
    explanation: str | None
    score_delta: int
    match_score: float
    match_type: MatchType


@dataclass(frozen=True)
class AnswerCandidate:
    """Normalized option or alias that can be matched against user input."""

    letter: AnswerLetter
    text: str
    normalized_text: str
    match_type: MatchType


def judge_answer(
    question: Question,
    *,
    answer_letter: str | None = None,
    answer_text: str | None = None,
    fuzzy_threshold: float = FUZZY_MATCH_THRESHOLD,
) -> JudgeResult:
    """Evaluate a letter or free-text answer against one ABCD question."""

    submitted_answer = _get_submitted_answer(answer_letter, answer_text)

    if answer_letter is not None:
        parsed_letter = parse_answer_letter(answer_letter)
        if parsed_letter is None:
            raise ValueError("answer_letter must resolve to A, B, C or D")
        return _build_result(question, submitted_answer, parsed_letter, 100.0, "letter")

    parsed_letter = parse_answer_letter(answer_text or "")
    if parsed_letter is not None:
        return _build_result(question, submitted_answer, parsed_letter, 100.0, "letter")

    normalized_answer = normalize_answer_text(answer_text or "")
    if not normalized_answer:
        raise ValueError("answer_text must not be empty when answer_letter is missing")

    candidates = _build_answer_candidates(question)

    exact_candidate = _find_exact_candidate(normalized_answer, candidates)
    if exact_candidate is not None:
        return _build_result(
            question,
            submitted_answer,
            exact_candidate.letter,
            100.0,
            exact_candidate.match_type,
        )

    fuzzy_candidate, fuzzy_score = _find_fuzzy_candidate(normalized_answer, candidates)
    if fuzzy_candidate is not None and fuzzy_score >= fuzzy_threshold:
        return _build_result(
            question,
            submitted_answer,
            fuzzy_candidate.letter,
            fuzzy_score,
            "fuzzy",
        )

    return _build_result(question, submitted_answer, None, 0.0, "none")


def parse_answer_letter(value: str) -> AnswerLetter | None:
    """Extract a single ABCD answer letter from raw user or STT text."""

    normalized_value = normalize_answer_text(value)
    if normalized_value in LETTER_WORDS:
        return LETTER_WORDS[normalized_value]

    tokens = normalized_value.split()
    letter_tokens = [token for token in tokens if token in LETTER_WORDS]
    if len(letter_tokens) != 1:
        return None

    if all(token in LETTER_FILLER_WORDS or token in LETTER_WORDS for token in tokens):
        return LETTER_WORDS[letter_tokens[0]]

    return None


def normalize_answer_text(value: str) -> str:
    """Normalize text for deterministic matching across casing and diacritics."""

    translated_value = value.translate(POLISH_CHARACTER_TRANSLATION)
    normalized_value = unicodedata.normalize("NFKD", translated_value)
    without_diacritics = "".join(
        character
        for character in normalized_value
        if not unicodedata.combining(character)
    )
    lower_value = without_diacritics.casefold()
    alphanumeric_value = re.sub(r"[^a-z0-9]+", " ", lower_value)
    return " ".join(alphanumeric_value.split())


def _get_submitted_answer(answer_letter: str | None, answer_text: str | None) -> str:
    """Choose the user-visible answer value for the response payload."""

    if answer_letter is not None and answer_letter.strip():
        return answer_letter.strip()

    if answer_text is not None and answer_text.strip():
        return answer_text.strip()

    raise ValueError("answer_letter or answer_text is required")


def _build_answer_candidates(question: Question) -> list[AnswerCandidate]:
    """Build normalized match candidates from options and aliases."""

    candidates: list[AnswerCandidate] = []

    for letter, option_text in question.options.items():
        candidates.append(
            AnswerCandidate(
                letter=letter,
                text=option_text,
                normalized_text=normalize_answer_text(option_text),
                match_type="option_text",
            )
        )

    for letter, aliases in question.aliases.items():
        for alias in aliases:
            candidates.append(
                AnswerCandidate(
                    letter=letter,
                    text=alias,
                    normalized_text=normalize_answer_text(alias),
                    match_type="alias",
                )
            )

    return candidates


def _find_exact_candidate(
    normalized_answer: str, candidates: list[AnswerCandidate]
) -> AnswerCandidate | None:
    """Return the candidate whose normalized text exactly matches input."""

    for candidate in candidates:
        if normalized_answer == candidate.normalized_text:
            return candidate

    return None


def _find_fuzzy_candidate(
    normalized_answer: str, candidates: list[AnswerCandidate]
) -> tuple[AnswerCandidate | None, float]:
    """Return the best fuzzy candidate and its RapidFuzz score."""

    best_candidate: AnswerCandidate | None = None
    best_score = 0.0

    for candidate in candidates:
        score = fuzz.ratio(normalized_answer, candidate.normalized_text)
        if score > best_score:
            best_candidate = candidate
            best_score = score

    return best_candidate, best_score


def _build_result(
    question: Question,
    submitted_answer: str,
    matched_answer: AnswerLetter | None,
    match_score: float,
    match_type: MatchType,
) -> JudgeResult:
    """Convert a matched answer into the public judge result shape."""

    is_correct = matched_answer == question.correct_answer

    return JudgeResult(
        question_id=question.id,
        submitted_answer=submitted_answer,
        matched_answer=cast(AnswerLetter | None, matched_answer),
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        score_delta=1 if is_correct else 0,
        match_score=round(match_score, 2),
        match_type=match_type,
    )
