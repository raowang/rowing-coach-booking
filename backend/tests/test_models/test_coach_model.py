"""Test coach model validation."""
import sys

import pytest

sys.path.insert(0, "/mnt/d/GitHub/ai/agent/reserve-app/rowing-coach-booking/backend")

from app.models.coach import (
    CoachBase,
    CoachCreate,
    CoachResponse,
    CoachUpdate,
    TeachingStyle,
)


class TestCoachModel:
    def test_coach_base_valid(self):
        coach = CoachBase(
            name="Test Coach",
            phone="13900139000",
            bio="Experienced coach",
            teaching_style=TeachingStyle.PROFESSIONAL,
            specialties=["technique", "endurance"],
        )
        assert coach.name == "Test Coach"
        assert coach.bio == "Experienced coach"
        assert coach.teaching_style == TeachingStyle.PROFESSIONAL
        assert coach.specialties == ["technique", "endurance"]

    def test_coach_base_defaults(self):
        coach = CoachBase(name="Minimal Coach")
        assert coach.name == "Minimal Coach"
        assert coach.phone is None
        assert coach.bio is None
        assert coach.teaching_style is None
        assert coach.specialties == []
        assert coach.rating == 5.0
        assert coach.review_count == 0
        assert coach.is_active is True

    def test_coach_create_valid(self):
        coach = CoachCreate(
            name="New Coach",
            teaching_style=TeachingStyle.PATIENT,
            specialties=["beginner training"],
        )
        assert coach.name == "New Coach"
        assert coach.teaching_style == TeachingStyle.PATIENT

    def test_coach_update_partial(self):
        update = CoachUpdate(name="Updated Coach")
        assert update.name == "Updated Coach"
        assert update.phone is None
        assert update.bio is None

    def test_coach_update_all_fields(self):
        update = CoachUpdate(
            name="Fully Updated",
            phone="13800138000",
            bio="New bio",
            teaching_style=TeachingStyle.STRICT,
            specialties=["speed training"],
            is_active=False,
        )
        assert update.name == "Fully Updated"
        assert update.phone == "13800138000"
        assert update.bio == "New bio"
        assert update.teaching_style == TeachingStyle.STRICT
        assert update.specialties == ["speed training"]
        assert update.is_active is False

    def test_coach_response_valid(self):
        response = CoachResponse(
            id="coach-123",
            name="Response Coach",
            rating=4.5,
            review_count=10,
        )
        assert response.id == "coach-123"
        assert response.name == "Response Coach"
        assert response.rating == 4.5
        assert response.review_count == 10

    def test_teaching_style_enum_values(self):
        assert TeachingStyle.PATIENT.value == "patient"
        assert TeachingStyle.PROFESSIONAL.value == "professional"
        assert TeachingStyle.STRICT.value == "strict"

    def test_coach_with_high_rating(self):
        coach = CoachBase(name="Top Coach", rating=4.9, review_count=100)
        assert coach.rating == 4.9
        assert coach.review_count == 100

    def test_coach_specialties_default_empty_list(self):
        coach = CoachBase(name="No Specialties Coach")
        assert coach.specialties == []

    def test_coach_update_with_specialties(self):
        update = CoachUpdate(specialties=["technique", "endurance", "speed"])
        assert update.specialties == ["technique", "endurance", "speed"]

    def test_coach_inactive_status(self):
        coach = CoachBase(name="Inactive Coach", is_active=False)
        assert coach.is_active is False
