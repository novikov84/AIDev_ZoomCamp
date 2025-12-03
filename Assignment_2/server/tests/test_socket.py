import asyncio
import socket

import httpx
import pytest
import pytest_asyncio
import socketio
import uvicorn

from app.main import application


@pytest_asyncio.fixture
async def live_server():
    try:
        probe = socket.socket()
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
        probe.close()
    except OSError:
        pytest.skip("Cannot bind to localhost port in this environment")

    config = uvicorn.Config(application, host="127.0.0.1", port=port, log_level="error", lifespan="off")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.05)
    if server.servers and server.servers[0].sockets:
        port = server.servers[0].sockets[0].getsockname()[1]
    base_url = f"http://127.0.0.1:{port}"
    yield base_url
    server.should_exit = True
    await asyncio.wait_for(task, timeout=5)


@pytest.mark.asyncio
async def test_socket_join_and_sync(live_server):
    base_url = live_server

    async with httpx.AsyncClient(base_url=base_url) as client:
        resp = await client.post("/api/session")
        resp.raise_for_status()
        session_id = resp.json()["sessionId"]

    client_a = socketio.AsyncClient()
    client_b = socketio.AsyncClient()

    received = asyncio.Event()
    payload = {}

    @client_b.on("code_update")
    async def on_code_update(data):
        payload.update(data or {})
        received.set()

    await client_a.connect(base_url, socketio_path="socket.io")
    await client_b.connect(base_url, socketio_path="socket.io")

    await client_a.emit("join", {"room": session_id})
    await client_b.emit("join", {"room": session_id})

    await client_a.emit("code_change", {"room": session_id, "code": "print('hi')"})

    await asyncio.wait_for(received.wait(), timeout=5)
    assert payload.get("code") == "print('hi')"

    await client_a.disconnect()
    await client_b.disconnect()
