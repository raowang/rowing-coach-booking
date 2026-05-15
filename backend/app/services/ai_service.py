import json
import logging
from typing import Any, Optional

from app.core.ollama import get_ollama_client

logger = logging.getLogger(__name__)

SIMPLE_MODEL = "llama3.1:8b"
COMPLEX_MODEL = "llama3.1:70b"
EMBEDDING_MODEL = "bge-m3"

SYSTEM_PROMPTS = {
    "user_agent": """你是一个友好的赛艇教练预约助手。你的职责是：
1. 帮助会员预约教练
2. 回答关于教练的问题
3. 收集训练反馈
4. 提供个性化的训练建议

请用友好、专业的语气与会员交流。始终基于提供的信息给出准确的回答。""",
    "coach_agent": """你是一个专业的赛艇教练管理助手。你的职责是：
1. 帮助教练管理日程
2. 协调预约确认
3. 收集教练点评
4. 提供训练建议

请用专业、高效的语气与教练交流。""",
    "recommendation": """你是一个赛艇教练推荐专家。基于会员的画像、偏好和历史数据，
推荐最合适的教练并解释推荐理由。"""
}


class AIService:
    def __init__(self):
        self.ollama = get_ollama_client()

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str = SIMPLE_MODEL,
        system: Optional[str] = None
    ) -> dict[str, Any]:
        if system:
            full_messages = [{"role": "system", "content": system}] + messages
        else:
            full_messages = messages

        try:
            response = await self.ollama.chat(model=model, messages=full_messages)
            return response
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            return {"error": str(e)}

    async def generate_welcome_message(
        self,
        member_name: str,
        skill_level: str,
        time_of_day: str
    ) -> str:
        time_greeting = self._get_time_greeting(time_of_day)
        skill_desc = self._get_skill_description(skill_level)

        prompt = f"""{time_greeting}，{member_name}！{skill_desc}

作为一个热情的赛艇教练预约助手，请生成一段欢迎语，介绍你可以帮助的功能：
- 预约教练
- 查看教练信息
- 管理预约
- 获取训练建议

请用亲切友好的语气，生成一段50字左右的欢迎语。"""

        try:
            response = await self.ollama.generate(
                model=SIMPLE_MODEL,
                prompt=prompt
            )
            return response.get("response", f"{time_greeting}，{member_name}！欢迎使用赛艇教练预约系统。")
        except Exception as e:
            logger.error(f"Welcome message generation error: {e}")
            return f"{time_greeting}，{member_name}！欢迎使用赛艇教练预约系统。"

    async def get_embeddings(self, text: str) -> list[float]:
        try:
            return await self.ollama.get_embeddings(model=EMBEDDING_MODEL, text=text)
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []

    async def generate_coach_recommendation_explanation(
        self,
        member_profile: dict,
        coach_profile: dict,
        reasoning: str
    ) -> str:
        prompt = f"""基于以下信息，生成一段推荐解释：

会员：{json.dumps(member_profile, ensure_ascii=False)}
教练：{json.dumps(coach_profile, ensure_ascii=False)}
匹配理由：{reasoning}

请生成一段简洁的推荐解释（50字以内），说明为什么这个教练适合这个会员。"""

        try:
            response = await self.ollama.generate(model=SIMPLE_MODEL, prompt=prompt)
            return response.get("response", reasoning)
        except Exception as e:
            logger.error(f"Recommendation explanation error: {e}")
            return reasoning

    def _get_time_greeting(self, time_of_day: str) -> str:
        greetings = {
            "morning": "早上好",
            "afternoon": "下午好",
            "evening": "晚上好",
            "night": "夜深了，注意休息哦"
        }
        return greetings.get(time_of_day, "你好")

    def _get_skill_description(self, skill_level: str) -> str:
        descriptions = {
            "beginner": "看到你是初学者，我会帮你找到耐心、专业的教练",
            "intermediate": "作为进阶学员，我会为你匹配更适合的教练",
            "advanced": "作为高级学员，我会为你安排专业训练"
        }
        return descriptions.get(skill_level, "")


ai_service = AIService()
