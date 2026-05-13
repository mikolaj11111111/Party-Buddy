import httpx
import pytest

from backend.app.core.stt import (
    SttConfig,
    SttUpstreamError,
    SttValidationError,
    transcribe_audio,
)


class FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, object]) -> None:
        self.status_code = status_code
        self.payload = payload

    def json(self) -> dict[str, object]:
        return self.payload


class FakeClient:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.request: dict[str, object] | None = None
        self.closed = False

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        data: dict[str, str],
        files: dict[str, tuple[str, bytes, str]],
    ) -> FakeResponse:
        self.request = {
            "url": url,
            "headers": headers,
            "data": data,
            "files": files,
        }
        return self.response

    def close(self) -> None:
        self.closed = True


def test_transcribe_audio_posts_audio_to_groq() -> None:
    config = SttConfig(
        api_key="test-key",
        model="whisper-large-v3-turbo",
        language="pl",
        endpoint_url="https://example.test/transcriptions",
    )
    client = FakeClient(FakeResponse(200, {"text": " odpowiedz A "}))

    result = transcribe_audio(
        b"audio-bytes",
        filename="answer.webm",
        content_type="audio/webm",
        config=config,
        client=client,  # type: ignore[arg-type]
    )

    assert result.text == "odpowiedz A"
    assert client.request == {
        "url": "https://example.test/transcriptions",
        "headers": {"Authorization": "Bearer test-key"},
        "data": {
            "model": "whisper-large-v3-turbo",
            "language": "pl",
            "response_format": "json",
            "temperature": "0",
        },
        "files": {"file": ("answer.webm", b"audio-bytes", "audio/webm")},
    }
    assert client.closed is False


def test_transcribe_audio_rejects_empty_file() -> None:
    config = SttConfig(api_key="test-key")

    with pytest.raises(SttValidationError):
        transcribe_audio(
            b"",
            filename="answer.webm",
            content_type="audio/webm",
            config=config,
        )


def test_transcribe_audio_rejects_too_large_file() -> None:
    config = SttConfig(api_key="test-key")

    with pytest.raises(SttValidationError):
        transcribe_audio(
            b"x" * (25 * 1024 * 1024 + 1),
            filename="answer.webm",
            content_type="audio/webm",
            config=config,
        )


def test_transcribe_audio_raises_for_upstream_error_status() -> None:
    config = SttConfig(api_key="test-key")
    client = FakeClient(FakeResponse(401, {"error": "unauthorized"}))

    with pytest.raises(SttUpstreamError, match="HTTP 401"):
        transcribe_audio(
            b"audio-bytes",
            filename="answer.webm",
            content_type="audio/webm",
            config=config,
            client=client,  # type: ignore[arg-type]
        )


def test_transcribe_audio_raises_for_network_error() -> None:
    class FailingClient:
        def post(self, *args: object, **kwargs: object) -> object:
            request = httpx.Request("POST", "https://example.test/transcriptions")
            raise httpx.ConnectError("network down", request=request)

        def close(self) -> None:
            pass

    config = SttConfig(api_key="test-key")

    with pytest.raises(SttUpstreamError, match="request failed"):
        transcribe_audio(
            b"audio-bytes",
            filename="answer.webm",
            content_type="audio/webm",
            config=config,
            client=FailingClient(),  # type: ignore[arg-type]
        )


def test_transcribe_audio_raises_when_response_has_no_text() -> None:
    config = SttConfig(api_key="test-key")
    client = FakeClient(FakeResponse(200, {"result": "missing"}))

    with pytest.raises(SttUpstreamError, match="missing text"):
        transcribe_audio(
            b"audio-bytes",
            filename="answer.webm",
            content_type="audio/webm",
            config=config,
            client=client,  # type: ignore[arg-type]
        )
