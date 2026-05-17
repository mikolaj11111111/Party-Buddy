from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.core.five_seconds_prompt_loader import load_five_seconds_prompts
from backend.app.main import app


def test_five_seconds_prompt_loader_reads_authored_dataset() -> None:
    prompts = load_five_seconds_prompts(Path("data/5_seconds/prompts.json"))

    assert len(prompts) == 120
    assert prompts[0].id.startswith("fs_")
    assert prompts[0].expected_answer_count == 3
    assert len(prompts[0].sample_answers) >= 3


def test_five_seconds_prompts_endpoint_returns_dataset() -> None:
    with TestClient(app) as client:
        response = client.get("/api/5-seconds/prompts")

    body = response.json()

    assert response.status_code == 200
    assert len(body) == 120
    assert set(body[0]) == {
        "id",
        "category",
        "difficulty",
        "prompt",
        "expected_answer_count",
        "sample_answers",
    }
