from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.answer import router as answer_router
from backend.app.api.game import router as game_router
from backend.app.api.ping import router as ping_router
from backend.app.api.stt import router as stt_router
from backend.app.api.tts import router as tts_router
from backend.app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Initialize app resources before serving requests."""

    init_db()
    yield


app = FastAPI(title="Part Buddy API", version="0.0.1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(ping_router)
app.include_router(answer_router)
app.include_router(game_router)
app.include_router(stt_router)
app.include_router(tts_router)


@app.get("/")
def root() -> dict[str, str]:
    """Return a small service identity payload."""

    return {"status": "ok", "service": "part-buddy", "version": "0.0.1"}


@app.get("/health")
def health() -> dict[str, str]:
    """Return a lightweight health check response."""

    return {"status": "healthy"}
