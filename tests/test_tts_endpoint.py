from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.api import tts as tts_api
from backend.app.core.tts import TtsCacheMissError, TtsValidationError
from backend.app.main import app


def test_tts_endpoint_returns_cached_wav(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key = "a" * 64
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"RIFFfake-wav")

    monkeypatch.setattr(tts_api, "resolve_cached_audio_path", lambda value: audio_path)

    with TestClient(app) as client:
        response = client.get(f"/api/tts?key={key}")

    assert response.status_code == 200
    assert response.content == b"RIFFfake-wav"
    assert response.headers["content-type"].startswith("audio/wav")


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (TtsValidationError("invalid TTS cache key"), 422),
        (TtsCacheMissError("TTS cache miss"), 404),
    ],
)
def test_tts_endpoint_maps_errors_to_http_status(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    expected_status: int,
) -> None:
    def fake_resolve_cached_audio_path(key: str) -> Path:
        raise error

    monkeypatch.setattr(
        tts_api,
        "resolve_cached_audio_path",
        fake_resolve_cached_audio_path,
    )

    with TestClient(app) as client:
        response = client.get(f"/api/tts?key={'a' * 64}")

    assert response.status_code == expected_status
    assert response.json()["detail"] == str(error)
