from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current UTC timestamp for SQLModel defaults."""

    return datetime.now(UTC)
