from fastapi import APIRouter, File, HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from backend.app.core.stt import (
    SttConfigurationError,
    SttUpstreamError,
    SttValidationError,
    transcribe_audio,
)
from backend.app.models.stt import SttResponse

router = APIRouter(prefix="/api/stt", tags=["stt"])


@router.post("", response_model=SttResponse)
async def transcribe(file: UploadFile = File(...)) -> SttResponse:
    audio_bytes = await file.read()

    try:
        result = await run_in_threadpool(
            transcribe_audio,
            audio_bytes,
            filename=file.filename or "audio.webm",
            content_type=file.content_type,
        )
    except SttValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except SttConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except SttUpstreamError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    return SttResponse(text=result.text)
