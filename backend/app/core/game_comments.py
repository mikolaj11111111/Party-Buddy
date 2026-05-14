from dataclasses import dataclass

from backend.app.core.tts import build_tts_cache_key, get_tts_config
from backend.app.core.tts_templates import COMMENT_TEMPLATES

COMMENT_TEMPLATE_BY_ID = {template.id: template for template in COMMENT_TEMPLATES}


@dataclass(frozen=True)
class GameComment:
    """Audio comment metadata that the frontend can resolve through /api/tts."""

    id: str
    key: str


def get_intro_comment() -> GameComment:
    """Return the first-round intro comment."""

    return _build_comment("intro_001")


def get_answer_comment(*, is_correct: bool, round_number: int) -> GameComment:
    """Return a deterministic correct/wrong comment for one resolved answer."""

    prefix = "correct" if is_correct else "wrong"
    index = ((round_number - 1) % 10) + 1
    return _build_comment(f"{prefix}_{index:03}")


def get_outro_comment() -> GameComment:
    """Return the session-finished outro comment."""

    return _build_comment("outro_001")


def _build_comment(template_id: str) -> GameComment:
    """Convert a comment template id into the current TTS cache key."""

    template = COMMENT_TEMPLATE_BY_ID[template_id]
    voice_id = get_tts_config().voice_id
    return GameComment(
        id=template.id,
        key=build_tts_cache_key(template.text, voice_id),
    )
