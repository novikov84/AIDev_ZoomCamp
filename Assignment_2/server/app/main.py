import os
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

ROOM_STATE: Dict[str, Dict[str, Any]] = {}

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
origins = os.getenv("CORS_ORIGINS", ",".join(default_origins)).split(",")
BASE_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = BASE_DIR / "dist"

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=origins,
    logger=False,
    engineio_logger=False,
)

app = FastAPI(title="Coding Interview Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],  # relaxed for dev/demo and Docker same-origin
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


if DIST_DIR.exists():
    # Serve the built Vite app in production/Docker
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/", response_class=HTMLResponse)
    async def serve_index() -> str:
        index_file = DIST_DIR / "index.html"
        if index_file.exists():
            return index_file.read_text(encoding="utf-8")
        return "<h1>Build not found</h1>"


application = socketio.ASGIApp(sio, other_asgi_app=app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:application", host="0.0.0.0", port=8000, reload=True)
