from fastapi import APIRouter, HTTPException

from backend.app.core.hangman_word_loader import (
    HangmanWordLoaderError,
    load_hangman_words,
)
from backend.app.models.hangman import HangmanWord

router = APIRouter(prefix="/api/hangman", tags=["hangman"])


@router.get("/words", response_model=list[HangmanWord])
def list_hangman_words() -> list[HangmanWord]:
    """Return the authored word bank for the Hangman game."""

    try:
        return load_hangman_words()
    except HangmanWordLoaderError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
