import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from backend.app.core.env import load_env_file
from backend.app.db import PROJECT_ROOT

DEFAULT_TTS_VOICE_ID = "pl_PL-gosia-medium"
TTS_CACHE_DIRECTORY = PROJECT_ROOT / "data" / "tts_cache"
TTS_VOICES_DIRECTORY = PROJECT_ROOT / "data" / "voices"
TTS_KEY_PATTERN = re.compile(r"^[a-f0-9]{64}$")


class TtsError(RuntimeError):
    pass


class TtsConfigurationError(TtsError):
    pass


class TtsValidationError(TtsError):
    pass


class TtsSynthesisError(TtsError):
    pass


class TtsCacheMissError(TtsError):
    pass


@dataclass(frozen=True)
class TtsConfig:
    voice_id: str
    model_path: Path
    config_path: Path
    cache_dir: Path = TTS_CACHE_DIRECTORY
    python_executable: str = sys.executable
    timeout_seconds: float = 90.0


@dataclass(frozen=True)
class TtsResult:
    key: str
    audio_path: Path
    generated: bool


def get_tts_config(voice_id: str | None = None) -> TtsConfig:
    load_env_file()

    selected_voice_id = (
        voice_id or os.environ.get("PIPER_VOICE_ID") or DEFAULT_TTS_VOICE_ID
    )
    voices_dir = Path(os.environ.get("PIPER_VOICES_DIR", TTS_VOICES_DIRECTORY))
    cache_dir = Path(os.environ.get("PIPER_TTS_CACHE_DIR", TTS_CACHE_DIRECTORY))

    return TtsConfig(
        voice_id=selected_voice_id,
        model_path=voices_dir / f"{selected_voice_id}.onnx",
        config_path=voices_dir / f"{selected_voice_id}.onnx.json",
        cache_dir=cache_dir,
        python_executable=os.environ.get("PIPER_PYTHON_EXECUTABLE", sys.executable),
    )


def validate_tts_text(text: str) -> str:
    normalized_text = " ".join(text.strip().split())
    if not normalized_text:
        raise TtsValidationError("TTS text must not be empty")

    if len(normalized_text) > 500:
        raise TtsValidationError("TTS text is too long")

    return normalized_text


def build_tts_cache_key(text: str, voice_id: str) -> str:
    normalized_text = validate_tts_text(text)
    payload = f"{voice_id}\n{normalized_text}".encode()
    return hashlib.sha256(payload).hexdigest()


def resolve_cached_audio_path(
    key: str,
    cache_dir: Path = TTS_CACHE_DIRECTORY,
) -> Path:
    if not TTS_KEY_PATTERN.fullmatch(key):
        raise TtsValidationError("invalid TTS cache key")

    resolved_cache_dir = cache_dir.resolve()
    audio_path = (resolved_cache_dir / f"{key}.wav").resolve()
    if not audio_path.is_relative_to(resolved_cache_dir):
        raise TtsValidationError("invalid TTS cache path")

    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise TtsCacheMissError(f"TTS cache miss: {key}")

    return audio_path


def synthesize_to_cache(
    text: str,
    config: TtsConfig | None = None,
) -> TtsResult:
    tts_config = config or get_tts_config()
    normalized_text = validate_tts_text(text)
    _validate_tts_config(tts_config)

    key = build_tts_cache_key(normalized_text, tts_config.voice_id)
    tts_config.cache_dir.mkdir(parents=True, exist_ok=True)
    audio_path = tts_config.cache_dir / f"{key}.wav"

    if audio_path.exists() and audio_path.stat().st_size > 0:
        return TtsResult(key=key, audio_path=audio_path, generated=False)

    temp_path = tts_config.cache_dir / f"{key}.tmp.wav"
    command = [
        tts_config.python_executable,
        "-m",
        "piper",
        "-m",
        str(tts_config.model_path),
        "-c",
        str(tts_config.config_path),
        "-f",
        str(temp_path),
        "--",
        normalized_text,
    ]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=tts_config.timeout_seconds,
        check=False,
    )
    if completed.returncode != 0:
        temp_path.unlink(missing_ok=True)
        error_output = completed.stderr.strip() or completed.stdout.strip()
        raise TtsSynthesisError(error_output or "Piper synthesis failed")

    if not temp_path.exists() or temp_path.stat().st_size == 0:
        temp_path.unlink(missing_ok=True)
        raise TtsSynthesisError("Piper did not create audio file")

    temp_path.replace(audio_path)
    return TtsResult(key=key, audio_path=audio_path, generated=True)


def _validate_tts_config(config: TtsConfig) -> None:
    if not config.model_path.exists():
        raise TtsConfigurationError(f"Piper voice model not found: {config.model_path}")

    if not config.config_path.exists():
        raise TtsConfigurationError(
            f"Piper voice config not found: {config.config_path}",
        )
