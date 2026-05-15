"""Test recommendation service business logic."""
import sys
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, "/mnt/d/GitHub/ai/agent/reserve-app/rowing-coach-booking/backend")

from app.models.booking import BookingStatus
from app.services.recommendation_service import (
    CoachProfile,
    MemberProfile,
    RecommendationService,
)


class TestMemberProfile:
    def test_member_profile_creation(self, sample_member_data: dict[str, Any]):
        profile = MemberProfile(sample_member_data)
        assert profile.id == "member-123"
        assert profile.name == "Test Member"
        assert profile.skill_level == "intermediate"
        assert profile.learning_style == "visual"

    def test_member_profile_defaults(self):
        minimal_data = {"id": "test-id", "name": "Test"}
        profile = MemberProfile(minimal_data)
        assert profile.skill_level == "beginner"
        assert profile.portrait_data == {}

    def test_member_profile_to_dict(self, sample_member_data: dict[str, Any]):
        profile = MemberProfile(sample_member_data)
        result = profile.to_dict()
        assert result["id"] == "member-123"
        assert result["name"] == "Test Member"
        assert "portrait_data" in result


class TestCoachProfile:
    def test_coach_profile_creation(self, sample_coach_data: dict[str, Any]):
        profile = CoachProfile(sample_coach_data)
        assert profile.id == "coach-456"
        assert profile.name == "Test Coach"
        assert profile.teaching_style == "professional"
        assert profile.specialties == ["technique", "endurance", "speed"]

    def test_coach_profile_defaults(self):
        minimal_data = {"id": "test-coach", "name": "Coach"}
        profile = CoachProfile(minimal_data)
        assert profile.rating == 5.0
        assert profile.review_count == 0
        assert profile.specialties == []

    def test_coach_profile_to_dict(self, sample_coach_data: dict[str, Any]):
        profile = CoachProfile(sample_coach_data)
        result = profile.to_dict()
        assert result["id"] == "coach-456"
        assert result["rating"] == 4.8


class TestRecommendationService:
    @pytest.fixture
    def service_with_mock_directus(self, mock_directus_client: MagicMock):
        service = RecommendationService()
        service.directus = mock_directus_client
        return service

    @pytest.mark.asyncio
    async def test_get_member_profile_found(
        self,
        service_with_mock_directus: RecommendationService,
        sample_member_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.get_item = AsyncMock(
            return_value={"data": sample_member_data}
        )
        profile = await service_with_mock_directus.get_member_profile("member-123")
        assert profile is not None
        assert profile.id == "member-123"
        assert profile.name == "Test Member"

    @pytest.mark.asyncio
    async def test_get_member_profile_not_found(
        self,
        service_with_mock_directus: RecommendationService,
    ):
        service_with_mock_directus.directus.get_item = AsyncMock(return_value={})
        profile = await service_with_mock_directus.get_member_profile("nonexistent")
        assert profile is None

    @pytest.mark.asyncio
    async def test_get_member_profile_error(
        self,
        service_with_mock_directus: RecommendationService,
    ):
        service_with_mock_directus.directus.get_item = AsyncMock(
            side_effect=Exception("DB Error")
        )
        profile = await service_with_mock_directus.get_member_profile("member-123")
        assert profile is None

    @pytest.mark.asyncio
    async def test_get_coach_profile_found(
        self,
        service_with_mock_directus: RecommendationService,
        sample_coach_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.get_item = AsyncMock(
            return_value={"data": sample_coach_data}
        )
        profile = await service_with_mock_directus.get_coach_profile("coach-456")
        assert profile is not None
        assert profile.id == "coach-456"

    def test_calculate_match_score_beginner_patient(self):
        service = RecommendationService()
        member = MemberProfile({"id": "1", "name": "Beginner", "skill_level": "beginner"})
        coach = CoachProfile({"id": "1", "name": "Patient Coach", "teaching_style": "patient", "rating": 5.0})
        score = service._calculate_match_score(member, coach)
        assert score >= 3.0

    def test_calculate_match_score_intermediate_professional(self):
        service = RecommendationService()
        member = MemberProfile({"id": "1", "name": "Intermediate", "skill_level": "intermediate"})
        coach = CoachProfile({"id": "1", "name": "Professional Coach", "teaching_style": "professional", "rating": 4.5})
        score = service._calculate_match_score(member, coach)
        assert score >= 3.0

    def test_calculate_match_score_advanced_strict(self):
        service = RecommendationService()
        member = MemberProfile({"id": "1", "name": "Advanced", "skill_level": "advanced"})
        coach = CoachProfile({"id": "1", "name": "Strict Coach", "teaching_style": "strict", "rating": 4.8})
        score = service._calculate_match_score(member, coach)
        assert score >= 3.0

    def test_calculate_match_score_specialties(self):
        service = RecommendationService()
        member = MemberProfile({
            "id": "1",
            "name": "Test",
            "skill_level": "beginner",
            "portrait_data": {"preferred_specialties": ["technique", "endurance"]}
        })
        coach = CoachProfile({
            "id": "1",
            "name": "Coach",
            "teaching_style": "patient",
            "specialties": ["technique", "speed"],
            "rating": 4.5
        })
        score = service._calculate_match_score(member, coach)
        assert score >= 3.5

    def test_calculate_match_score_personality_match(self):
        service = RecommendationService()
        member = MemberProfile({
            "id": "1",
            "name": "Test",
            "skill_level": "beginner",
            "personality_preference": "patient"
        })
        coach = CoachProfile({
            "id": "1",
            "name": "Coach",
            "teaching_style": "patient",
            "rating": 4.0
        })
        score = service._calculate_match_score(member, coach)
        assert score >= 5.0

    def test_calculate_match_score_rating_bonus(self):
        service = RecommendationService()
        member = MemberProfile({"id": "1", "name": "Test", "skill_level": "beginner"})
        coach_high = CoachProfile({"id": "1", "name": "High Rated", "teaching_style": "patient", "rating": 4.8})
        coach_low = CoachProfile({"id": "2", "name": "Low Rated", "teaching_style": "patient", "rating": 4.0})
        score_high = service._calculate_match_score(member, coach_high)
        score_low = service._calculate_match_score(member, coach_low)
        assert score_high > score_low

    def test_get_match_reasons_beginner_patient(self):
        service = RecommendationService()
        member = MemberProfile({"id": "1", "name": "Beginner", "skill_level": "beginner"})
        coach = CoachProfile({"id": "1", "name": "Patient Coach", "teaching_style": "patient", "rating": 4.8})
        reasons = service._get_match_reasons(member, coach)
        assert any("耐心" in r or "初学者" in r for r in reasons)

    def test_get_match_reasons_high_rating(self):
        service = RecommendationService()
        member = MemberProfile({"id": "1", "name": "Test", "skill_level": "beginner"})
        coach = CoachProfile({"id": "1", "name": "Coach", "teaching_style": "patient", "rating": 4.8})
        reasons = service._get_match_reasons(member, coach)
        assert any("4.8" in r for r in reasons)

    @pytest.mark.asyncio
    async def test_recommend_coaches_returns_results(
        self,
        service_with_mock_directus: RecommendationService,
        sample_member_data: dict[str, Any],
        sample_coach_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.get_item = AsyncMock(
            return_value={"data": sample_member_data}
        )
        service_with_mock_directus.directus.query = AsyncMock(
            return_value={"data": [sample_coach_data]}
        )
        results = await service_with_mock_directus.recommend_coaches("member-123", limit=5)
        assert len(results) > 0
        assert "match_score" in results[0]

    @pytest.mark.asyncio
    async def test_recommend_coaches_no_member(
        self,
        service_with_mock_directus: RecommendationService,
    ):
        service_with_mock_directus.directus.get_item = AsyncMock(return_value={})
        results = await service_with_mock_directus.recommend_coaches("nonexistent")
        assert results == []

    @pytest.mark.asyncio
    async def test_get_member_booking_history(
        self,
        service_with_mock_directus: RecommendationService,
        sample_booking_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.query = AsyncMock(
            return_value={"data": [sample_booking_data]}
        )
        history = await service_with_mock_directus.get_member_booking_history("member-123")
        assert len(history) == 1
        assert history[0]["status"] == "pending"
