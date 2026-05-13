import os
from dataclasses import dataclass
from pathlib import Path

import httpx

from backend.app.db import PROJECT_ROOT

GROQ_TRANSCRIPTIONS_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
DEFAULT_STT_MODEL = "whisper-large-v3-turbo"
DEFAULT_STT_LANGUAGE = "pl"
MAX_AUDIO_BYTES = 25 * 1024 * 1024


class SttError(RuntimeError):
    pass


class SttConfigurationError(SttError):
    pass


class SttValidationError(SttError):
    pass


class SttUpstreamError(SttError):
    pass


@dataclass(frozen=True)
class SttConfig:
    api_key: str
    model: str = DEFAULT_STT_MODEL
    language: str = DEFAULT_STT_LANGUAGE
    endpoint_url: str = GROQ_TRANSCRIPTIONS_URL
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class SttResult:
    text: str


def load_env_file(env_path: Path = PROJECT_ROOT / ".env") -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def get_stt_config() -> SttConfig:
    load_env_file()

    api_key = os.environ.get("GROQ_WHISPER_API")
    if not api_key:
        raise SttConfigurationError("GROQ_WHISPER_API is not configured")

    return SttConfig(
        api_key=api_key,
        model=os.environ.get("GROQ_WHISPER_MODEL", DEFAULT_STT_MODEL),
        language=os.environ.get("GROQ_WHISPER_LANGUAGE", DEFAULT_STT_LANGUAGE),
        endpoint_url=os.environ.get("GROQ_WHISPER_URL", GROQ_TRANSCRIPTIONS_URL),
    )


def transcribe_audio(
    audio_bytes: bytes,
    *,
    filename: str,
    content_type: str | None,
    config: SttConfig | None = None,
    client: httpx.Client | None = None,
) -> SttResult:
    if not audio_bytes:
        raise SttValidationError("audio file must not be empty")

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise SttValidationError("audio file is too large")

    stt_config = config or get_stt_config()
    filename = filename.strip() or "audio.webm"
    media_type = content_type or "application/octet-stream"

    should_close_client = client is None
    if client is None:
        client = httpx.Client(timeout=stt_config.timeout_seconds)

    try:
        response = client.post(
            stt_config.endpoint_url,
            headers={"Authorization": f"Bearer {stt_config.api_key}"},
            data={
                "model": stt_config.model,
                "language": stt_config.language,
                "response_format": "json",
                "temperature": "0",
            },
            files={"file": (filename, audio_bytes, media_type)},
        )
    except httpx.RequestError as error:
        raise SttUpstreamError("Groq STT request failed") from error
    finally:
        if should_close_client:
            client.close()

    if response.status_code >= 400:
        raise SttUpstreamError(f"Groq STT returned HTTP {response.status_code}")

    try:
        payload = response.json()
    except ValueError as error:
        raise SttUpstreamError("Groq STT returned invalid JSON") from error

    text = payload.get("text")
    if not isinstance(text, str):
        raise SttUpstreamError("Groq STT response is missing text")

    return SttResult(text=text.strip())
