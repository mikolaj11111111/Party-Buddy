import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.tts import synthesize_to_cache  # noqa: E402
from backend.app.core.tts_templates import iter_tts_templates  # noqa: E402


def main() -> None:
    for template in iter_tts_templates():
        result = synthesize_to_cache(template.text)
        status = "generated" if result.generated else "cached"
        print(f"{status}: {template.id} -> {result.key}")


if __name__ == "__main__":
    main()
