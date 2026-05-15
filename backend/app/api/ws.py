import json
import logging
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

from app.services.ai_service import ai_service, SYSTEM_PROMPTS
from app.core.database import valkey_client

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

    def get_context_key(self, session_id: str) -> str:
        return f"chat_context:{session_id}"


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)

    context_key = manager.get_context_key(session_id)

    if valkey_client:
        cached_context = valkey_client.get(context_key)
        if cached_context and isinstance(cached_context, str):
            context = json.loads(cached_context)
        else:
            context = []
    else:
        context = []

    try:
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id
        })

        while True:
            data = await websocket.receive_json()

            if data.get("type") == "message":
                member_id = data.get("member_id")
                content = data.get("content")

                if not member_id or not content:
                    await websocket.send_json({
                        "type": "error",
                        "message": "member_id and content are required"
                    })
                    continue

                messages = context + [{"role": "user", "content": content}]

                system_prompt = SYSTEM_PROMPTS["user_agent"]
                messages_with_system = [{"role": "system", "content": system_prompt}] + messages

                try:
                    result = await ai_service.chat(messages=messages_with_system)

                    if "error" in result:
                        await websocket.send_json({
                            "type": "error",
                            "message": result["error"]
                        })
                    else:
                        ai_response = result.get("message", {}).get("content", "")

                        context.append({"role": "user", "content": content})
                        context.append({"role": "assistant", "content": ai_response})

                        if len(context) > 20:
                            context = context[-20:]

                        if valkey_client:
                            valkey_client.setex(context_key, 3600, json.dumps(context))

                        await websocket.send_json({
                            "type": "message",
                            "content": ai_response,
                            "context_updated": True
                        })

                except Exception as e:
                    logger.error(f"Chat error: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })

            elif data.get("type") == "clear_context":
                context = []
                if valkey_client:
                    valkey_client.delete(context_key)
                await websocket.send_json({
                    "type": "context_cleared"
                })

            elif data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong"
                })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)
