import pytest
import asyncio
import websockets
from typing import AsyncGenerator


@pytest.fixture
async def websocket_client() -> AsyncGenerator:
    uri = "ws://localhost:8000/chat"
    async with websockets.connect(uri) as websocket:
        yield websocket


@pytest.mark.asyncio
async def test_chat_initial_greeting(websocket_client):
    # Test initial greeting
    response = await websocket_client.recv()
    assert "Hello!" in response
    assert "research topic" in response.lower()


@pytest.mark.asyncio
async def test_chat_conversation_flow(websocket_client):
    # Receive initial greeting
    await websocket_client.recv()

    # Test conversation flow
    test_messages = [
        "I'm interested in machine learning applications in healthcare",
        "Specifically focusing on medical imaging",
        "done"
    ]

    for message in test_messages:
        await websocket_client.send(message)
        response = await websocket_client.recv()
        assert response is not None
        assert len(response) > 0


@pytest.mark.asyncio
async def test_chat_exit_commands(websocket_client):
    # Receive initial greeting
    await websocket_client.recv()

    # Test exit commands
    await websocket_client.send("done")
    response = await websocket_client.recv()
    assert "Final Refined Search Criteria" in response


if __name__ == "__main__":
    asyncio.run(pytest.main([__file__]))