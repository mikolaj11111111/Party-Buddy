import json
from pathlib import Path

from pydantic import ValidationError

from backend.app.db import PROJECT_ROOT
from backend.app.models.five_seconds import FiveSecondsPrompt

FIVE_SECONDS_PROMPTS_PATH = PROJECT_ROOT / "data" / "5_seconds" / "prompts.json"


class FiveSecondsPromptLoaderError(ValueError):
    """Raised when 5 Seconds prompt data cannot be loaded or validated."""

    pass


def load_five_seconds_prompts(
    prompts_path: Path = FIVE_SECONDS_PROMPTS_PATH,
) -> list[FiveSecondsPrompt]:
    """Load and validate the 5 Seconds prompt dataset."""

    if not prompts_path.exists():
        raise FiveSecondsPromptLoaderError(
            f"5 seconds prompts file does not exist: {prompts_path}"
        )

    try:
        raw_prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise FiveSecondsPromptLoaderError(
            f"invalid JSON in {prompts_path}: {error}"
        ) from error

    if not isinstance(raw_prompts, list):
        raise FiveSecondsPromptLoaderError(
            f"5 seconds prompts file must contain a list: {prompts_path}"
        )

    prompts: list[FiveSecondsPrompt] = []
    seen_ids: set[str] = set()
    for index, raw_prompt in enumerate(raw_prompts):
        try:
            prompt = FiveSecondsPrompt.model_validate(raw_prompt)
        except ValidationError as error:
            raise FiveSecondsPromptLoaderError(
                f"invalid 5 seconds prompt at {prompts_path}:{index}: {error}"
            ) from error

        if prompt.id in seen_ids:
            raise FiveSecondsPromptLoaderError(
                f"duplicate 5 seconds prompt id: {prompt.id}"
            )

        seen_ids.add(prompt.id)
        prompts.append(prompt)

    if not prompts:
        raise FiveSecondsPromptLoaderError(
            f"no 5 seconds prompts found in: {prompts_path}"
        )

    return prompts
