import pytest
from fastapi.testclient import TestClient

from backend.app.api import stt as stt_api
from backend.app.core.stt import (
    SttConfigurationError,
    SttResult,
    SttUpstreamError,
    SttValidationError,
)
from backend.app.main import app


def test_stt_endpoint_returns_transcribed_text(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_transcribe_audio(
        audio_bytes: bytes,
        *,
        filename: str,
        content_type: str | None,
    ) -> SttResult:
        captured["audio_bytes"] = audio_bytes
        captured["filename"] = filename
        captured["content_type"] = content_type
        return SttResult(text="odpowiedz A")

    monkeypatch.setattr(stt_api, "transcribe_audio", fake_transcribe_audio)

    with TestClient(app) as client:
        response = client.post(
            "/api/stt",
            files={"file": ("answer.webm", b"audio-bytes", "audio/webm")},
        )

    assert response.status_code == 200
    assert response.json() == {"text": "odpowiedz A"}
    assert captured == {
        "audio_bytes": b"audio-bytes",
        "filename": "answer.webm",
        "content_type": "audio/webm",
    }


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (SttValidationError("audio file must not be empty"), 422),
        (SttConfigurationError("GROQ_WHISPER_API is not configured"), 503),
        (SttUpstreamError("Groq STT returned HTTP 500"), 502),
    ],
)
def test_stt_endpoint_maps_errors_to_http_status(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    expected_status: int,
) -> None:
    def fake_transcribe_audio(
        audio_bytes: bytes,
        *,
        filename: str,
        content_type: str | None,
    ) -> SttResult:
        raise error

    monkeypatch.setattr(stt_api, "transcribe_audio", fake_transcribe_audio)

    with TestClient(app) as client:
        response = client.post(
            "/api/stt",
            files={"file": ("answer.webm", b"audio-bytes", "audio/webm")},
        )

    assert response.status_code == expected_status
    assert response.json()["detail"] == str(error)
