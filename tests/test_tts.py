import subprocess
from pathlib import Path

import pytest

from backend.app.core import tts
from backend.app.core.tts import (
    TtsCacheMissError,
    TtsConfig,
    TtsConfigurationError,
    TtsSynthesisError,
    TtsValidationError,
    build_tts_cache_key,
    resolve_cached_audio_path,
    synthesize_to_cache,
)


def make_config(tmp_path: Path) -> TtsConfig:
    voices_dir = tmp_path / "voices"
    voices_dir.mkdir()
    model_path = voices_dir / "test_voice.onnx"
    config_path = voices_dir / "test_voice.onnx.json"
    model_path.write_bytes(b"model")
    config_path.write_text("{}", encoding="utf-8")

    return TtsConfig(
        voice_id="test_voice",
        model_path=model_path,
        config_path=config_path,
        cache_dir=tmp_path / "cache",
        python_executable="python",
    )


def test_build_tts_cache_key_is_stable() -> None:
    key = build_tts_cache_key("  Dobra   odpowiedź. ", "pl_PL-gosia-medium")

    assert key == build_tts_cache_key("Dobra odpowiedź.", "pl_PL-gosia-medium")
    assert len(key) == 64


def test_synthesize_to_cache_generates_wav(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    config = make_config(tmp_path)

    def fake_run(
        command: list[str],
        *,
        capture_output: bool,
        text: bool,
        timeout: float,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        output_path = Path(command[command.index("-f") + 1])
        output_path.write_bytes(b"RIFFfake-wav")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(tts.subprocess, "run", fake_run)

    result = synthesize_to_cache("Testowy komentarz.", config=config)

    assert result.generated is True
    assert result.audio_path.exists()
    assert result.audio_path.read_bytes() == b"RIFFfake-wav"
    assert captured["command"] == [
        "python",
        "-m",
        "piper",
        "-m",
        str(config.model_path),
        "-c",
        str(config.config_path),
        "-f",
        str(config.cache_dir / f"{result.key}.tmp.wav"),
        "--",
        "Testowy komentarz.",
    ]


def test_synthesize_to_cache_reuses_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = make_config(tmp_path)
    key = build_tts_cache_key("Testowy komentarz.", config.voice_id)
    config.cache_dir.mkdir()
    audio_path = config.cache_dir / f"{key}.wav"
    audio_path.write_bytes(b"cached")

    def fail_run(*args: object, **kwargs: object) -> None:
        raise AssertionError("subprocess.run should not be called")

    monkeypatch.setattr(tts.subprocess, "run", fail_run)

    result = synthesize_to_cache("Testowy komentarz.", config=config)

    assert result.generated is False
    assert result.audio_path == audio_path


def test_synthesize_to_cache_raises_when_voice_model_is_missing(
    tmp_path: Path,
) -> None:
    config = TtsConfig(
        voice_id="missing_voice",
        model_path=tmp_path / "missing.onnx",
        config_path=tmp_path / "missing.onnx.json",
        cache_dir=tmp_path / "cache",
    )

    with pytest.raises(TtsConfigurationError):
        synthesize_to_cache("Test.", config=config)


def test_synthesize_to_cache_raises_when_piper_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = make_config(tmp_path)

    def fake_run(
        command: list[str],
        *,
        capture_output: bool,
        text: bool,
        timeout: float,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="boom")

    monkeypatch.setattr(tts.subprocess, "run", fake_run)

    with pytest.raises(TtsSynthesisError, match="boom"):
        synthesize_to_cache("Test.", config=config)


def test_validate_tts_text_rejects_empty_text() -> None:
    with pytest.raises(TtsValidationError):
        synthesize_to_cache("   ")


def test_resolve_cached_audio_path_returns_existing_file(tmp_path: Path) -> None:
    key = "a" * 64
    audio_path = tmp_path / f"{key}.wav"
    audio_path.write_bytes(b"RIFF")

    assert resolve_cached_audio_path(key, tmp_path) == audio_path.resolve()


def test_resolve_cached_audio_path_rejects_invalid_key(tmp_path: Path) -> None:
    with pytest.raises(TtsValidationError):
        resolve_cached_audio_path("../secret", tmp_path)


def test_resolve_cached_audio_path_raises_for_cache_miss(tmp_path: Path) -> None:
    with pytest.raises(TtsCacheMissError):
        resolve_cached_audio_path("a" * 64, tmp_path)
