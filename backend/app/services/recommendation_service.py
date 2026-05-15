import logging
from typing import Optional

from app.core.directus import get_directus_client
from app.models import (
    CoachResponse,
    MemberResponse,
    BookingStatus,
)

logger = logging.getLogger(__name__)


class MemberProfile:
    def __init__(self, member_data: dict):
        self.id = member_data.get("id")
        self.name = member_data.get("name")
        self.skill_level = member_data.get("skill_level", "beginner")
        self.learning_style = member_data.get("learning_style")
        self.personality_preference = member_data.get("personality_preference")
        self.portrait_data = member_data.get("portrait_data", {})

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "skill_level": self.skill_level,
            "learning_style": self.learning_style,
            "personality_preference": self.personality_preference,
            "portrait_data": self.portrait_data
        }


class CoachProfile:
    def __init__(self, coach_data: dict):
        self.id = coach_data.get("id")
        self.name = coach_data.get("name")
        self.teaching_style = coach_data.get("teaching_style")
        self.specialties = coach_data.get("specialties", [])
        self.rating = coach_data.get("rating", 5.0)
        self.review_count = coach_data.get("review_count", 0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "teaching_style": self.teaching_style,
            "specialties": self.specialties,
            "rating": self.rating,
            "review_count": self.review_count
        }


class RecommendationService:
    def __init__(self):
        self.directus = get_directus_client()

    async def get_member_profile(self, member_id: str) -> Optional[MemberProfile]:
        try:
            result = await self.directus.get_item("members", member_id)
            if result and "data" in result:
                return MemberProfile(result["data"])
            return None
        except Exception as e:
            logger.error(f"Error fetching member profile: {e}")
            return None

    async def get_coach_profile(self, coach_id: str) -> Optional[CoachProfile]:
        try:
            result = await self.directus.get_item("coaches", coach_id)
            if result and "data" in result:
                return CoachProfile(result["data"])
            return None
        except Exception as e:
            logger.error(f"Error fetching coach profile: {e}")
            return None

    async def recommend_coaches(
        self,
        member_id: str,
        limit: int = 5
    ) -> list[dict]:
        member_profile = await self.get_member_profile(member_id)
        if not member_profile:
            return []

        try:
            result = await self.directus.query(
                "coaches",
                filter={"is_active": {"_eq": True}},
                sort=["-rating"],
                limit=limit * 2
            )

            coaches = result.get("data", [])
            scored_coaches = []

            for coach_data in coaches:
                score = self._calculate_match_score(member_profile, CoachProfile(coach_data))
                coach_data["match_score"] = score
                coach_data["match_reasons"] = self._get_match_reasons(member_profile, CoachProfile(coach_data))
                scored_coaches.append(coach_data)

            scored_coaches.sort(key=lambda x: x["match_score"], reverse=True)
            return scored_coaches[:limit]

        except Exception as e:
            logger.error(f"Error recommending coaches: {e}")
            return []

    def _calculate_match_score(self, member: MemberProfile, coach: CoachProfile) -> float:
        score = 0.0

        if member.skill_level == "beginner" and coach.teaching_style == "patient":
            score += 3.0
        elif member.skill_level == "intermediate" and coach.teaching_style == "professional":
            score += 3.0
        elif member.skill_level == "advanced" and coach.teaching_style == "strict":
            score += 3.0

        common_specialties = set(member.portrait_data.get("preferred_specialties", [])) & set(coach.specialties)
        score += len(common_specialties) * 0.5

        if member.personality_preference == coach.teaching_style:
            score += 2.0

        score += (coach.rating - 4.0) * 2.0

        return score

    def _get_match_reasons(self, member: MemberProfile, coach: CoachProfile) -> list[str]:
        reasons = []

        if member.skill_level == "beginner" and coach.teaching_style == "patient":
            reasons.append("教练风格耐心细致，适合初学者")
        elif member.skill_level == "intermediate" and coach.teaching_style == "professional":
            reasons.append("教练专业能力强，适合进阶训练")
        elif member.skill_level == "advanced" and coach.teaching_style == "strict":
            reasons.append("教练要求严格，适合高水平训练")

        common_specialties = set(member.portrait_data.get("preferred_specialties", [])) & set(coach.specialties)
        if common_specialties:
            reasons.append(f"擅长{','.join(list(common_specialties)[:2])}")

        if coach.rating >= 4.5:
            reasons.append(f"评分高达{coach.rating}分")

        return reasons

    async def get_member_booking_history(
        self,
        member_id: str,
        limit: int = 10
    ) -> list[dict]:
        try:
            result = await self.directus.query(
                "bookings",
                filter={
                    "member_id": {"_eq": member_id},
                    "status": {"_in": [BookingStatus.COMPLETED.value, BookingStatus.CONFIRMED.value]}
                },
                sort=["-scheduled_time"],
                limit=limit
            )
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Error fetching booking history: {e}")
            return []


recommendation_service = RecommendationService()
