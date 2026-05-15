"""
Integration Tests for Rowing Coach Booking API

Tests end-to-end workflows:
- Member registration and booking flow
- Coach scheduling and confirmation
- Training feedback loop

Run with: pytest tests/test_integration.py -v
"""

import pytest
from httpx import AsyncClient


BASE_URL = "http://localhost:8000"


class TestMemberBookingFlow:
    """Test complete member booking flow."""

    @pytest.mark.asyncio
    async def test_full_booking_workflow(self):
        """Test complete flow: register -> browse coaches -> book -> confirm -> complete."""
        async with AsyncClient(base_url=BASE_URL) as client:
            member_data = {
                "openid": f"test-member-{id(self)}",
                "name": "Test Member",
                "phone": "13800138000",
                "skill_level": "beginner",
            }

            member_response = await client.post("/api/v1/members/", json=member_data)
            assert member_response.status_code == 201
            member = member_response.json()
            member_id = member["id"]

            coaches_response = await client.get("/api/v1/coaches/")
            assert coaches_response.status_code == 200
            coaches = coaches_response.json()
            assert len(coaches) > 0
            coach_id = coaches[0]["id"]

            booking_data = {
                "openid": member_data["openid"],
                "coach_id": coach_id,
                "scheduled_time": "2025-12-25 10:00",
            }
            booking_response = await client.post("/api/v1/bookings/", json=booking_data)
            assert booking_response.status_code == 201
            booking = booking_response.json()
            booking_id = booking["id"]
            assert booking["status"] == "pending"

            confirm_response = await client.post(
                f"/api/v1/bookings/{booking_id}/confirm",
                json={"coach_id": coach_id},
            )
            assert confirm_response.status_code == 200
            confirmed = confirm_response.json()
            assert confirmed["status"] == "confirmed"


class TestCoachScheduleFlow:
    """Test coach schedule management."""

    @pytest.mark.asyncio
    async def test_coach_availability(self):
        """Test checking coach availability."""
        async with AsyncClient(base_url=BASE_URL) as client:
            coaches_response = await client.get("/api/v1/coaches/")
            if coaches_response.status_code != 200 or len(coaches_response.json()) == 0:
                pytest.skip("No coaches available")

            coach_id = coaches_response.json()[0]["id"]

            availability_response = await client.get(
                "/api/v1/schedules/available",
                params={"coach_id": coach_id, "date": "2025-12-25"},
            )
            assert availability_response.status_code == 200


class TestTrainingFeedbackFlow:
    """Test training feedback loop."""

    @pytest.mark.asyncio
    async def test_training_record_creation(self):
        """Test creating training record after booking."""
        async with AsyncClient(base_url=BASE_URL) as client:
            booking_response = await client.get(
                "/api/v1/bookings",
                params={"status": "completed"},
            )
            if booking_response.status_code != 200:
                pytest.skip("No completed bookings")

            bookings = booking_response.json()
            if len(bookings) == 0:
                pytest.skip("No completed bookings")

            booking = bookings[0]

            feedback_data = {
                "booking_id": booking["id"],
                "member_id": booking["member_id"],
                "coach_id": booking["coach_id"],
                "rating": 5,
                "coach_comment": "Great progress!",
            }
            feedback_response = await client.post(
                "/api/v1/training-records/", json=feedback_data
            )
            assert feedback_response.status_code == 201


class TestAIFeatures:
    """Test AI-related features."""

    @pytest.mark.asyncio
    async def test_welcome_message(self):
        """Test AI welcome message generation."""
        async with AsyncClient(base_url=BASE_URL) as client:
            welcome_response = await client.post(
                "/api/v1/ai/welcome",
                json={
                    "openid": "test-user",
                    "member_name": "Test User",
                    "skill_level": "beginner",
                },
            )
            assert welcome_response.status_code == 200
            assert "welcome_message" in welcome_response.json()

    @pytest.mark.asyncio
    async def test_chat(self):
        """Test AI chat endpoint."""
        async with AsyncClient(base_url=BASE_URL) as client:
            chat_response = await client.post(
                "/api/v1/ai/chat",
                json={
                    "openid": "test-user",
                    "message": "你好",
                    "context": [],
                },
            )
            assert chat_response.status_code == 200
            assert "response" in chat_response.json()

    @pytest.mark.asyncio
    async def test_coach_recommendation(self):
        """Test AI coach recommendation."""
        async with AsyncClient(base_url=BASE_URL) as client:
            rec_response = await client.post(
                "/api/v1/ai/recommend-coach",
                json={
                    "openid": "test-user",
                    "skill_level": "beginner",
                    "limit": 3,
                },
            )
            assert rec_response.status_code == 200
            result = rec_response.json()
            assert "recommendations" in result or "recommendation" in result


class TestEngagementFeatures:
    """Test member engagement features."""

    @pytest.mark.asyncio
    async def test_birthday_check(self):
        """Test birthday greeting trigger."""
        async with AsyncClient(base_url=BASE_URL) as client:
            engagement_response = await client.get(
                "/api/v1/ai/engagement/birthday-check",
                params={"date": "2025-06-15"},
            )
            assert engagement_response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_renewal_check(self):
        """Test membership renewal reminder trigger."""
        async with AsyncClient(base_url=BASE_URL) as client:
            renewal_response = await client.get(
                "/api/v1/ai/engagement/renewal-check",
                params={"days_until": 7},
            )
            assert renewal_response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])