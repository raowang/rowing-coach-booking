import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1 import members, coaches, bookings, schedules, ai, training_records

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Rowing Coach Booking API...")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="赛艇教练预约系统后端API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(members.router, prefix=settings.api_v1_prefix)
app.include_router(coaches.router, prefix=settings.api_v1_prefix)
app.include_router(bookings.router, prefix=settings.api_v1_prefix)
app.include_router(schedules.router, prefix=settings.api_v1_prefix)
app.include_router(ai.router, prefix=settings.api_v1_prefix)
app.include_router(training_records.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {"message": "Rowing Coach Booking API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.websocket("/ws/chat/{session_id}")
async def ws_chat(websocket, session_id: str):
    from app.api.ws import websocket_endpoint
    await websocket_endpoint(websocket, session_id)