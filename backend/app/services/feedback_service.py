import json
import logging
from typing import Optional

from app.core.directus import get_directus_client
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class FeedbackService:
    def __init__(self):
        self.directus = get_directus_client()

    async def create_training_record(
        self,
        booking_id: str,
        member_id: str,
        coach_id: str,
        rating: int,
        coach_comment: Optional[str] = None
    ) -> Optional[dict]:
        try:
            ai_suggestions = await self.generate_ai_suggestions(
                member_id=member_id,
                coach_id=coach_id,
                rating=rating,
                coach_comment=coach_comment
            )

            result = await self.directus.create_item("training_records", {
                "booking_id": booking_id,
                "member_id": member_id,
                "coach_id": coach_id,
                "rating": rating,
                "coach_comment": coach_comment,
                "ai_suggestions": ai_suggestions
            })
            return result.get("data")
        except Exception as e:
            logger.error(f"Error creating training record: {e}")
            return None

    async def update_training_record(
        self,
        record_id: str,
        rating: Optional[int] = None,
        coach_comment: Optional[str] = None,
        ai_suggestions: Optional[dict] = None
    ) -> Optional[dict]:
        update_data = {}
        if rating is not None:
            update_data["rating"] = rating
        if coach_comment is not None:
            update_data["coach_comment"] = coach_comment
        if ai_suggestions is not None:
            update_data["ai_suggestions"] = ai_suggestions

        try:
            result = await self.directus.update_item("training_records", record_id, update_data)
            return result.get("data")
        except Exception as e:
            logger.error(f"Error updating training record: {e}")
            return None

    async def get_training_record(self, record_id: str) -> Optional[dict]:
        try:
            result = await self.directus.get_item("training_records", record_id)
            return result.get("data")
        except Exception as e:
            logger.error(f"Error fetching training record: {e}")
            return None

    async def get_member_training_history(
        self,
        member_id: str,
        limit: int = 20
    ) -> list[dict]:
        try:
            result = await self.directus.query(
                "training_records",
                filter={"member_id": {"_eq": member_id}},
                sort=["-created_at"],
                limit=limit
            )
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Error fetching training history: {e}")
            return []

    async def generate_ai_suggestions(
        self,
        member_id: str,
        coach_id: str,
        rating: int,
        coach_comment: Optional[str] = None
    ) -> dict:
        member_profile = await self._get_member_profile(member_id)
        coach_profile = await self._get_coach_profile(coach_id)
        recent_records = await self.get_member_training_history(member_id, limit=5)

        prompt = self._build_suggestion_prompt(
            member_profile,
            coach_profile,
            rating,
            coach_comment,
            recent_records
        )

        try:
            response = await ai_service.ollama.generate(
                model="llama3.1:8b",
                prompt=prompt
            )
            suggestions_text = response.get("response", "")

            return self._parse_suggestions(suggestions_text)
        except Exception as e:
            logger.error(f"Error generating AI suggestions: {e}")
            return {"error": "Failed to generate suggestions"}

    def _build_suggestion_prompt(
        self,
        member_profile: dict,
        coach_profile: dict,
        rating: int,
        coach_comment: Optional[str],
        recent_records: list[dict]
    ) -> str:
        recent_summary = []
        for record in recent_records:
            summary = f"- 评分{record.get('rating')}"
            coach_comment = record.get('coach_comment')
            if coach_comment and isinstance(coach_comment, str):
                summary += f"，教练点评：{coach_comment[:50]}"
            recent_summary.append(summary)

        prompt = f"""基于以下信息，生成训练改善建议：

会员信息：
- 技术水平：{member_profile.get('skill_level', '未知')}
- 学习风格：{member_profile.get('learning_style', '未知')}

教练信息：
- 姓名：{coach_profile.get('name', '未知')}
- 教学风格：{coach_profile.get('teaching_style', '未知')}
- 专长：{','.join(coach_profile.get('specialties', []))}

本次训练：
- 评分：{rating}/5
- 教练点评：{coach_comment or '无'}

历史训练：
{chr(10).join(recent_summary) if recent_summary else '暂无历史记录'}

请生成2-3条具体的训练改善建议，以JSON格式返回，格式如下：
{{
    "suggestions": [
        {{"area": "技术", "suggestion": "具体建议"}},
        {{"area": "体能", "suggestion": "具体建议"}},
        {{"area": "心理", "suggestion": "具体建议"}}
    ],
    "next_training_focus": "下次训练重点"
}}

只返回JSON，不要有其他内容。"""
        return prompt

    def _parse_suggestions(self, response_text: str) -> dict:
        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start != -1 and json_end != 0:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing suggestions JSON: {e}")

        return {
            "suggestions": [
                {"area": "训练", "suggestion": "建议继续规律训练，保持积极态度"}
            ],
            "next_training_focus": "基础技术巩固"
        }

    async def _get_member_profile(self, member_id: str) -> dict:
        try:
            result = await self.directus.get_item("members", member_id)
            return result.get("data", {})
        except Exception:
            return {}

    async def _get_coach_profile(self, coach_id: str) -> dict:
        try:
            result = await self.directus.get_item("coaches", coach_id)
            return result.get("data", {})
        except Exception:
            return {}


feedback_service = FeedbackService()
