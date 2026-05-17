from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.core.hangman_word_loader import load_hangman_words
from backend.app.main import app


def test_hangman_word_loader_reads_authored_dataset() -> None:
    words = load_hangman_words(Path("data/hangman/words.json"))

    assert len(words) == 195
    assert words[0].id.startswith("hangman_")
    assert words[0].word
    assert words[0].hint


def test_hangman_words_endpoint_returns_dataset() -> None:
    with TestClient(app) as client:
        response = client.get("/api/hangman/words")

    body = response.json()

    assert response.status_code == 200
    assert len(body) == 195
    assert set(body[0]) == {
        "id",
        "category",
        "difficulty",
        "word",
        "hint",
    }
