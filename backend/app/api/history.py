from fastapi import APIRouter, Depends, Query
from sqlmodel import Session as DbSession

from backend.app.core.game_history import list_finished_game_sessions
from backend.app.db import get_session
from backend.app.models.history import GameHistorySession

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/sessions", response_model=list[GameHistorySession])
def list_session_history(
    limit: int = Query(default=20, ge=1, le=100),
    db_session: DbSession = Depends(get_session),
) -> list[GameHistorySession]:
    """Return recent finished local game sessions."""

    return list_finished_game_sessions(db_session, limit=limit)
