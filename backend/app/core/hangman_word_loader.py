import json
from pathlib import Path

from pydantic import ValidationError

from backend.app.db import PROJECT_ROOT
from backend.app.models.hangman import HangmanWord

HANGMAN_WORDS_PATH = PROJECT_ROOT / "data" / "hangman" / "words.json"


class HangmanWordLoaderError(ValueError):
    """Raised when Hangman word data cannot be loaded or validated."""

    pass


def load_hangman_words(
    words_path: Path = HANGMAN_WORDS_PATH,
) -> list[HangmanWord]:
    """Load and validate the Hangman word dataset."""

    if not words_path.exists():
        raise HangmanWordLoaderError(f"hangman words file does not exist: {words_path}")

    try:
        raw_words = json.loads(words_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise HangmanWordLoaderError(
            f"invalid JSON in {words_path}: {error}"
        ) from error

    if not isinstance(raw_words, list):
        raise HangmanWordLoaderError(
            f"hangman words file must contain a list: {words_path}"
        )

    words: list[HangmanWord] = []
    seen_ids: set[str] = set()
    for index, raw_word in enumerate(raw_words):
        try:
            word = HangmanWord.model_validate(raw_word)
        except ValidationError as error:
            raise HangmanWordLoaderError(
                f"invalid hangman word at {words_path}:{index}: {error}"
            ) from error

        if word.id in seen_ids:
            raise HangmanWordLoaderError(f"duplicate hangman word id: {word.id}")

        seen_ids.add(word.id)
        words.append(word)

    if not words:
        raise HangmanWordLoaderError(f"no hangman words found in: {words_path}")

    return words
