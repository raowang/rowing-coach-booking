"""Test bookings API endpoints."""
import sys
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, "/mnt/d/GitHub/ai/agent/reserve-app/rowing-coach-booking/backend")


class TestBookingsAPI:
    @pytest.fixture
    def mock_directus(self, mock_directus_client: MagicMock):
        return mock_directus_client

    @pytest.fixture
    def mock_scheduling_service(self):
        with patch("app.api.v1.bookings.scheduling_service") as mock:
            yield mock

    @pytest.fixture
    def client(self, mock_directus: MagicMock, mock_scheduling_service: MagicMock):
        with patch("app.core.directus.get_directus_client", return_value=mock_directus):
            with patch("app.api.v1.bookings.get_directus_client", return_value=mock_directus):
                with patch("app.api.v1.bookings.scheduling_service", mock_scheduling_service):
                    from fastapi import FastAPI
                    from app.api.v1.bookings import router
                    app = FastAPI()
                    app.include_router(router)
                    with TestClient(app) as c:
                        yield c

    def test_create_booking_success(
        self,
        client: TestClient,
        mock_scheduling_service: MagicMock,
        sample_booking_data: dict[str, Any],
    ):
        mock_scheduling_service.create_booking = AsyncMock(
            return_value=sample_booking_data
        )
        response = client.post("/", json={
            "member_id": "member-123",
            "coach_id": "coach-456",
            "scheduled_time": "2024-06-01T10:00:00Z",
            "end_time": "2024-06-01T11:00:00Z",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["member_id"] == "member-123"

    def test_create_booking_conflict(
        self,
        client: TestClient,
        mock_scheduling_service: MagicMock,
    ):
        mock_scheduling_service.create_booking = AsyncMock(return_value=None)
        response = client.post("/", json={
            "member_id": "member-123",
            "coach_id": "coach-456",
            "scheduled_time": "2024-06-01T10:00:00Z",
            "end_time": "2024-06-01T11:00:00Z",
        })
        assert response.status_code == 409

    def test_get_booking_found(
        self,
        client: TestClient,
        mock_directus: MagicMock,
        sample_booking_data: dict[str, Any],
    ):
        mock_directus.get_item = AsyncMock(return_value={"data": sample_booking_data})
        with patch("app.api.v1.bookings.directus.get_item", mock_directus.get_item):
            response = client.get("/booking-789")
            assert response.status_code == 200

    def test_get_booking_not_found(
        self,
        client: TestClient,
        mock_directus: MagicMock,
    ):
        mock_directus.get_item = AsyncMock(return_value={"data": None})
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_list_bookings(
        self,
        client: TestClient,
        mock_directus: MagicMock,
        sample_booking_data: dict[str, Any],
    ):
        mock_directus.query = AsyncMock(return_value={"data": [sample_booking_data]})
        mock_directus.get_item = AsyncMock(
            side_effect=[
                {"data": {"id": "member-123", "name": "Test Member"}},
                {"data": {"id": "coach-456", "name": "Test Coach"}},
            ]
        )
        response = client.get("/")
        assert response.status_code == 200

    def test_list_bookings_with_member_filter(
        self,
        client: TestClient,
        mock_directus: MagicMock,
    ):
        mock_directus.query = AsyncMock(return_value={"data": []})
        response = client.get("/?member_id=member-123")
        assert response.status_code == 200

    def test_list_bookings_with_status_filter(
        self,
        client: TestClient,
        mock_directus: MagicMock,
    ):
        mock_directus.query = AsyncMock(return_value={"data": []})
        response = client.get("/?status=pending")
        assert response.status_code == 200

    def test_confirm_booking_success(
        self,
        client: TestClient,
        mock_scheduling_service: MagicMock,
        sample_confirmed_booking_data: dict[str, Any],
    ):
        mock_scheduling_service.confirm_booking = AsyncMock(
            return_value=sample_confirmed_booking_data
        )
        response = client.post("/booking-790/confirm")
        assert response.status_code == 200

    def test_confirm_booking_not_found(
        self,
        client: TestClient,
        mock_scheduling_service: MagicMock,
    ):
        mock_scheduling_service.confirm_booking = AsyncMock(return_value=None)
        response = client.post("/nonexistent/confirm")
        assert response.status_code == 404

    def test_reject_booking_success(
        self,
        client: TestClient,
        mock_scheduling_service: MagicMock,
    ):
        mock_scheduling_service.reject_booking = AsyncMock(
            return_value={"status": "rejected"}
        )
        response = client.post("/booking-789/reject?reason=Schedule conflict")
        assert response.status_code == 200

    def test_cancel_booking_success(
        self,
        client: TestClient,
        mock_scheduling_service: MagicMock,
    ):
        mock_scheduling_service.cancel_booking = AsyncMock(
            return_value={"status": "cancelled"}
        )
        response = client.post("/booking-789/cancel")
        assert response.status_code == 200

    def test_start_training_success(
        self,
        client: TestClient,
        mock_scheduling_service: MagicMock,
        sample_in_progress_booking_data: dict[str, Any],
    ):
        mock_scheduling_service.start_training = AsyncMock(
            return_value=sample_in_progress_booking_data
        )
        response = client.post("/booking-791/start")
        assert response.status_code == 200

    def test_complete_training_success(
        self,
        client: TestClient,
        mock_scheduling_service: MagicMock,
        sample_completed_booking_data: dict[str, Any],
    ):
        mock_scheduling_service.complete_training = AsyncMock(
            return_value=sample_completed_booking_data
        )
        response = client.post("/booking-792/complete")
        assert response.status_code == 200

    def test_update_booking_status_to_confirmed(
        self,
        client: TestClient,
        mock_scheduling_service: MagicMock,
        sample_booking_data: dict[str, Any],
        sample_confirmed_booking_data: dict[str, Any],
    ):
        mock_scheduling_service.get_booking = AsyncMock(return_value=sample_booking_data)
        mock_scheduling_service.confirm_booking = AsyncMock(
            return_value=sample_confirmed_booking_data
        )
        response = client.patch("/booking-789", json={"status": "confirmed"})
        assert response.status_code == 200

    def test_update_booking_not_found(
        self,
        client: TestClient,
        mock_scheduling_service: MagicMock,
    ):
        mock_scheduling_service.get_booking = AsyncMock(return_value=None)
        response = client.patch("/nonexistent", json={"status": "confirmed"})
        assert response.status_code == 404
