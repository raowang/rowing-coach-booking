"""Shared fixtures for backend tests."""
import sys
from datetime import date, datetime
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

# Add backend/app to path for imports
sys.path.insert(0, "/mnt/d/GitHub/ai/agent/reserve-app/rowing-coach-booking/backend")


@pytest.fixture
def mock_directus_client():
    """Create a mock Directus client."""
    mock_client = MagicMock()
    mock_client.get_item = AsyncMock(return_value={"data": None})
    mock_client.create_item = AsyncMock(return_value={"data": None})
    mock_client.update_item = AsyncMock(return_value={"data": None})
    mock_client.delete_item = AsyncMock(return_value={"data": None})
    mock_client.query = AsyncMock(return_value={"data": []})
    return mock_client


@pytest.fixture
def mock_valkey_client():
    """Create a mock Valkey/Redis client."""
    mock_client = MagicMock()
    mock_client.exists = MagicMock(return_value=False)
    mock_client.setex = MagicMock(return_value=True)
    return mock_client


@pytest.fixture
def sample_member_data() -> dict[str, Any]:
    """Sample member data for tests."""
    return {
        "id": "member-123",
        "openid": "wechat_openid_123",
        "name": "Test Member",
        "phone": "13800138000",
        "gender": "male",
        "birthday": "1990-05-15",
        "membership_start": "2024-01-01",
        "membership_end": "2025-01-01",
        "skill_level": "intermediate",
        "learning_style": "visual",
        "personality_preference": "patient",
        "portrait_data": {"preferred_specialties": ["technique", "endurance"]},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_coach_data() -> dict[str, Any]:
    """Sample coach data for tests."""
    return {
        "id": "coach-456",
        "name": "Test Coach",
        "phone": "13900139000",
        "photo_url": "https://example.com/photo.jpg",
        "bio": "Experienced rowing coach",
        "teaching_style": "professional",
        "specialties": ["technique", "endurance", "speed"],
        "rating": 4.8,
        "review_count": 25,
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_booking_data() -> dict[str, Any]:
    """Sample booking data for tests."""
    return {
        "id": "booking-789",
        "member_id": "member-123",
        "coach_id": "coach-456",
        "scheduled_time": "2024-06-01T10:00:00Z",
        "end_time": "2024-06-01T11:00:00Z",
        "status": "pending",
        "created_at": "2024-05-15T00:00:00Z",
        "confirmed_at": None,
        "completed_at": None,
    }


@pytest.fixture
def sample_confirmed_booking_data() -> dict[str, Any]:
    """Sample confirmed booking data for tests."""
    return {
        "id": "booking-790",
        "member_id": "member-123",
        "coach_id": "coach-456",
        "scheduled_time": "2024-06-02T10:00:00Z",
        "end_time": "2024-06-02T11:00:00Z",
        "status": "confirmed",
        "created_at": "2024-05-15T00:00:00Z",
        "confirmed_at": "2024-05-16T00:00:00Z",
        "completed_at": None,
    }


@pytest.fixture
def sample_in_progress_booking_data() -> dict[str, Any]:
    """Sample in-progress booking data for tests."""
    return {
        "id": "booking-791",
        "member_id": "member-123",
        "coach_id": "coach-456",
        "scheduled_time": "2024-06-03T10:00:00Z",
        "end_time": "2024-06-03T11:00:00Z",
        "status": "in_progress",
        "created_at": "2024-05-15T00:00:00Z",
        "confirmed_at": "2024-05-16T00:00:00Z",
        "completed_at": None,
    }


@pytest.fixture
def sample_completed_booking_data() -> dict[str, Any]:
    """Sample completed booking data for tests."""
    return {
        "id": "booking-792",
        "member_id": "member-123",
        "coach_id": "coach-456",
        "scheduled_time": "2024-06-04T10:00:00Z",
        "end_time": "2024-06-04T11:00:00Z",
        "status": "completed",
        "created_at": "2024-05-15T00:00:00Z",
        "confirmed_at": "2024-05-16T00:00:00Z",
        "completed_at": "2024-06-04T11:30:00Z",
    }


@pytest.fixture
def app_mock():
    """Mock FastAPI app for API testing."""
    with patch("app.main.app"):
        yield


@pytest_asyncio.fixture
async def mock_directus_dependency(mock_directus_client):
    """Override get_directus_client dependency in API routes."""
    with patch("app.core.directus.get_directus_client", return_value=mock_directus_client):
        yield mock_directus_client


@pytest_asyncio.fixture
async def mock_valkey_dependency(mock_valkey_client):
    """Override valkey_client dependency in services."""
    with patch("app.core.database.valkey_client", mock_valkey_client):
        yield mock_valkey_client
