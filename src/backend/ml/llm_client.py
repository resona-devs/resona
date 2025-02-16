import ollama
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()


# WebSocket manager to handle multiple users
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


# Interactive chat to refine user research query
async def interactive_refine_user_query(websocket: WebSocket):
    await manager.send_personal_message("Hello! What topic are you interested in?", websocket)
    user_query = await websocket.receive_text()

    conversation = [
        {"role": "system",
         "content": "You are an expert AI research assistant helping a user refine their research query for finding relevant papers on arXiv."},
        {"role": "user", "content": user_query}
    ]

    while True:
        response = ollama.chat(model='mistral', messages=conversation)
        bot_message = response['message']['content']

        await manager.send_personal_message(bot_message, websocket)
        user_reply = await websocket.receive_text()

        if user_reply.lower() in ["done", "stop", "exit"]:
            break

        conversation.append({"role": "user", "content": user_reply})

    return response['message']['content']


@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        refined_query = await interactive_refine_user_query(websocket)
        await manager.send_personal_message(f"Refined Search Criteria: {refined_query}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)