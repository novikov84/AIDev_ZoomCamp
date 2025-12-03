import os
from typing import Any, Dict
from uuid import uuid4

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOM_STATE: Dict[str, Dict[str, Any]] = {}

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=origins,
    logger=False,
    engineio_logger=False,
)

app = FastAPI(title="Coding Interview Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],  # relaxed for dev/demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/session")
async def create_session() -> dict:
    session_id = uuid4().hex[:8]
    ROOM_STATE[session_id] = {"code": "// shared session\n", "language": "javascript"}
    return {"sessionId": session_id}


@sio.event
async def connect(sid, environ):
    # No auth for demo; log connection.
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def join(sid, data):
    room = data.get("room") if isinstance(data, dict) else None
    if not room:
        return
    await sio.enter_room(sid, room)
    state = ROOM_STATE.get(room)
    if state:
        await sio.emit("state_sync", state, room=sid)


@sio.event
async def code_change(sid, data):
    room = data.get("room") if isinstance(data, dict) else None
    code = data.get("code", "") if isinstance(data, dict) else ""
    if not room:
        return
    ROOM_STATE.setdefault(room, {})["code"] = code
    await sio.emit("code_update", {"code": code}, room=room, skip_sid=sid)


@sio.event
async def language_change(sid, data):
    room = data.get("room") if isinstance(data, dict) else None
    language = data.get("language") if isinstance(data, dict) else None
    if not room or not language:
        return
    ROOM_STATE.setdefault(room, {})["language"] = language
    await sio.emit("language_update", {"language": language}, room=room, skip_sid=sid)


application = socketio.ASGIApp(sio, other_asgi_app=app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:application", host="0.0.0.0", port=8000, reload=True)
