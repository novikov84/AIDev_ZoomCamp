import pytest
from app.main import application


@pytest.mark.skip("Socket integration test placeholder until in-process ASGI socket harness is wired")
@pytest.mark.asyncio
async def test_socket_join_and_sync():
    # TODO: add ASGI server fixture and socketio AsyncClient targeting TestClient server.
    assert True
