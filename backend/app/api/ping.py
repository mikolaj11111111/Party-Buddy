from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from backend.app.db import get_session
from backend.app.models import Ping

router = APIRouter(prefix="/api/ping", tags=["ping"])


@router.post("", response_model=Ping)
def create_ping(session: Session = Depends(get_session)) -> Ping:
    """Create a dummy ping row for the early SQLite smoke test."""

    ping = Ping()
    session.add(ping)
    session.commit()
    session.refresh(ping)
    return ping


@router.get("", response_model=list[Ping])
def list_pings(session: Session = Depends(get_session)) -> list[Ping]:
    """List dummy ping rows from the SQLite smoke test table."""

    return list(session.exec(select(Ping).order_by(Ping.id.desc())).all())
