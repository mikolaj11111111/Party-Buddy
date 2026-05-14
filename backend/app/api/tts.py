from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse

from backend.app.core.tts import (
    TtsCacheMissError,
    TtsValidationError,
    resolve_cached_audio_path,
)

router = APIRouter(prefix="/api/tts", tags=["tts"])


@router.get("", response_class=FileResponse)
def get_tts_audio(key: str = Query(min_length=64, max_length=64)) -> FileResponse:
    """Return one pre-generated WAV file by TTS cache key."""

    try:
        audio_path = resolve_cached_audio_path(key)
    except TtsValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except TtsCacheMissError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename=f"{key}.wav",
    )
