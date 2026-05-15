from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.directus import get_directus_client
from app.models import TrainingRecordCreate, TrainingRecordUpdate, TrainingRecordResponse
from app.services.ai_service import ai_service, SYSTEM_PROMPTS
from app.services.recommendation_service import recommendation_service
from app.services.feedback_service import feedback_service

router = APIRouter(prefix="/ai", tags=["ai"])
directus = get_directus_client()


class ChatRequest(BaseModel):
    member_id: str
    message: str
    context: Optional[list[dict]] = None


class ChatResponse(BaseModel):
    response: str
    context_updated: bool = False


class RecommendCoachRequest(BaseModel):
    member_id: str
    limit: Optional[int] = 5


class RecommendCoachResponse(BaseModel):
    coaches: list[dict]


class WelcomeRequest(BaseModel):
    member_id: str


class WelcomeResponse(BaseModel):
    message: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    member = await _get_member(request.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    messages = request.context or []
    messages.append({"role": "user", "content": request.message})

    system_prompt = SYSTEM_PROMPTS["user_agent"]
    member_context = f"会员信息：{member.get('name', '未知')}, 技术水平：{member.get('skill_level', '未知')}"
    messages_with_context = [{"role": "system", "content": f"{system_prompt}\n\n{member_context}"}] + messages

    result = await ai_service.chat(messages=messages_with_context)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    ai_response = result.get("message", {}).get("content", "抱歉，我现在无法回复。")

    return ChatResponse(
        response=ai_response,
        context_updated=True
    )


@router.post("/recommend-coach", response_model=RecommendCoachResponse)
async def recommend_coach(request: RecommendCoachRequest):
    coaches = await recommendation_service.recommend_coaches(
        member_id=request.member_id,
        limit=request.limit or 5
    )

    return RecommendCoachResponse(coaches=coaches)


@router.post("/welcome", response_model=WelcomeResponse)
async def welcome(request: WelcomeRequest):
    member = await _get_member(request.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    now = datetime.now()
    time_of_day = _get_time_of_day(now.hour)

    message = await ai_service.generate_welcome_message(
        member_name=member.get("name", "会员"),
        skill_level=member.get("skill_level", "beginner"),
        time_of_day=time_of_day
    )

    return WelcomeResponse(message=message)


async def _get_member(member_id: str) -> Optional[dict]:
    try:
        result = await directus.get_item("members", member_id)
        return result.get("data")
    except Exception:
        return None


def _get_time_of_day(hour: int) -> str:
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"
