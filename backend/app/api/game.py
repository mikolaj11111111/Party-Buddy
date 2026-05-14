from fastapi import APIRouter, WebSocket

from backend.app.core.game_realtime import GameWebSocketConnection

router = APIRouter(tags=["game"])


@router.websocket("/ws/game")
async def game_websocket(websocket: WebSocket) -> None:
    """Run one bidirectional realtime game session over WebSocket."""

    await GameWebSocketConnection().run(websocket)
