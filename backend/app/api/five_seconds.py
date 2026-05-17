from fastapi import APIRouter, HTTPException

from backend.app.core.five_seconds_prompt_loader import (
    FiveSecondsPromptLoaderError,
    load_five_seconds_prompts,
)
from backend.app.models.five_seconds import FiveSecondsPrompt

router = APIRouter(prefix="/api/5-seconds", tags=["5-seconds"])


@router.get("/prompts", response_model=list[FiveSecondsPrompt])
def list_five_seconds_prompts() -> list[FiveSecondsPrompt]:
    """Return the authored prompt bank for the 5 Seconds game."""

    try:
        return load_five_seconds_prompts()
    except FiveSecondsPromptLoaderError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
