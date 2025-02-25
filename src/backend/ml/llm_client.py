# main.py
import logging
from typing import List
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from lib.ollama.model_service import ModelService
from lib.ollama.config_service import ConfigService, ModelConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Query Refinement Service")


class ChatMessage(BaseModel):
    role: str
    content: str


model_service = ModelService()
config_service = ConfigService()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            logger.info(f"New connection established. Active connections: {len(self.active_connections)}")
        except Exception as e:
            logger.error(f"Error accepting connection: {str(e)}")
            raise

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Connection closed. Active connections: {len(self.active_connections)}")

    async def send_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise


manager = ConnectionManager()


@app.get("/models")
async def list_models():
    """List available models."""
    models = await model_service.list_models()
    return {"models": models}


@app.post("/model/set")
async def set_model(config: ModelConfig):
    """Set and pull a specific model."""
    success = await model_service.pull_model(config.model_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to pull model {config.model_name}")
    config_service.set_config(config)
    return {"status": "success", "model": config.model_name}


@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    config = config_service.get_config()
    system_prompt = model_service.get_system_prompt(config.prompt_type)

    conversation = [
        ChatMessage(role="system", content=system_prompt)
    ]

    try:
        # Initial greeting
        await manager.send_message(
            "Hello! What would you like to explore?",
            websocket
        )

        while True:
            user_message = await websocket.receive_text()

            if user_message.lower() in ["done", "stop", "exit"]:
                final_response = await model_service.generate_response(
                    [{"role": msg.role, "content": msg.content} for msg in conversation]
                )
                await manager.send_message(
                    f"Final Response: {final_response}",
                    websocket
                )
                break

            conversation.append(ChatMessage(role="user", content=user_message))

            bot_response = await model_service.generate_response(
                [{"role": msg.role, "content": msg.content} for msg in conversation]
            )
            conversation.append(ChatMessage(role="assistant", content=bot_response))
            await manager.send_message(bot_response, websocket)

    except WebSocketDisconnect:
        logger.info("Client disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error in chat session: {str(e)}")
        await manager.send_message(
            "An error occurred. Please try again later.",
            websocket
        )
        manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)