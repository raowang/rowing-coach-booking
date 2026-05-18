import json
import logging
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

from app.services.ai_service import ai_service, SYSTEM_PROMPTS

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.context_cache: dict[str, list] = {}

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

    def get_context(self, session_id: str) -> list:
        return self.context_cache.get(session_id, [])

    def set_context(self, session_id: str, context: list):
        self.context_cache[session_id] = context

    def clear_context(self, session_id: str):
        if session_id in self.context_cache:
            del self.context_cache[session_id]


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)

    context = manager.get_context(session_id)

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

                        manager.set_context(session_id, context)

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
                manager.clear_context(session_id)
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