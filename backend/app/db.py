from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "part_buddy.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create local SQLite tables for all registered SQLModel models."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    from backend.app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    """Yield one SQLModel session for FastAPI dependencies."""

    with Session(engine) as session:
        yield session
