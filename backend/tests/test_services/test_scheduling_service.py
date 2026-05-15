"""Test scheduling service and booking state machine."""
import sys
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, "/mnt/d/GitHub/ai/agent/reserve-app/rowing-coach-booking/backend")

from app.models.booking import BookingStatus
from app.services.scheduling_service import SchedulingService


class TestSchedulingService:
    @pytest.fixture
    def service_with_mock_directus(self, mock_directus_client: MagicMock):
        service = SchedulingService()
        service.directus = mock_directus_client
        return service

    @pytest.mark.asyncio
    async def test_check_availability_no_conflicts(
        self,
        service_with_mock_directus: SchedulingService,
    ):
        service_with_mock_directus.directus.query = AsyncMock(return_value={"data": []})
        available = await service_with_mock_directus.check_availability(
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
        )
        assert available is True

    @pytest.mark.asyncio
    async def test_check_availability_with_conflict(
        self,
        service_with_mock_directus: SchedulingService,
        sample_booking_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.query = AsyncMock(
            return_value={"data": [sample_booking_data]}
        )
        available = await service_with_mock_directus.check_availability(
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
        )
        assert available is False

    @pytest.mark.asyncio
    async def test_create_booking_success(
        self,
        service_with_mock_directus: SchedulingService,
        sample_booking_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.query = AsyncMock(return_value={"data": []})
        service_with_mock_directus.directus.create_item = AsyncMock(
            return_value={"data": sample_booking_data}
        )
        result = await service_with_mock_directus.create_booking(
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
        )
        assert result is not None
        assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_booking_conflict(
        self,
        service_with_mock_directus: SchedulingService,
        sample_booking_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.query = AsyncMock(
            return_value={"data": [sample_booking_data]}
        )
        result = await service_with_mock_directus.create_booking(
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_confirm_booking_success(
        self,
        service_with_mock_directus: SchedulingService,
        sample_confirmed_booking_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.update_item = AsyncMock(
            return_value={"data": sample_confirmed_booking_data}
        )
        result = await service_with_mock_directus.confirm_booking("booking-790")
        assert result is not None
        assert result["status"] == "confirmed"

    @pytest.mark.asyncio
    async def test_reject_booking_success(
        self,
        service_with_mock_directus: SchedulingService,
    ):
        service_with_mock_directus.directus.update_item = AsyncMock(
            return_value={"data": {"status": "rejected", "id": "booking-789"}}
        )
        result = await service_with_mock_directus.reject_booking("booking-789", "Schedule conflict")
        assert result is not None
        assert result["status"] == "rejected"

    @pytest.mark.asyncio
    async def test_cancel_booking_success(
        self,
        service_with_mock_directus: SchedulingService,
    ):
        service_with_mock_directus.directus.update_item = AsyncMock(
            return_value={"data": {"status": "cancelled", "id": "booking-789"}}
        )
        result = await service_with_mock_directus.cancel_booking("booking-789")
        assert result is not None
        assert result["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_start_training_success(
        self,
        service_with_mock_directus: SchedulingService,
        sample_in_progress_booking_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.update_item = AsyncMock(
            return_value={"data": sample_in_progress_booking_data}
        )
        result = await service_with_mock_directus.start_training("booking-791")
        assert result is not None
        assert result["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_complete_training_success(
        self,
        service_with_mock_directus: SchedulingService,
        sample_completed_booking_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.update_item = AsyncMock(
            return_value={"data": sample_completed_booking_data}
        )
        result = await service_with_mock_directus.complete_training("booking-792")
        assert result is not None
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_booking_found(
        self,
        service_with_mock_directus: SchedulingService,
        sample_booking_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.get_item = AsyncMock(
            return_value={"data": sample_booking_data}
        )
        result = await service_with_mock_directus.get_booking("booking-789")
        assert result is not None
        assert result["id"] == "booking-789"

    @pytest.mark.asyncio
    async def test_get_booking_not_found(
        self,
        service_with_mock_directus: SchedulingService,
    ):
        service_with_mock_directus.directus.get_item = AsyncMock(return_value={"data": None})
        result = await service_with_mock_directus.get_booking("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_pending_bookings(
        self,
        service_with_mock_directus: SchedulingService,
        sample_booking_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.query = AsyncMock(
            return_value={"data": [sample_booking_data]}
        )
        results = await service_with_mock_directus.get_pending_bookings()
        assert len(results) == 1
        assert results[0]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_pending_bookings_by_coach(
        self,
        service_with_mock_directus: SchedulingService,
        sample_booking_data: dict[str, Any],
    ):
        service_with_mock_directus.directus.query = AsyncMock(
            return_value={"data": [sample_booking_data]}
        )
        results = await service_with_mock_directus.get_pending_bookings(coach_id="coach-456")
        assert len(results) == 1


class TestBookingStateMachine:
    def test_next_status_pending_to_confirmed(self):
        service = SchedulingService()
        next_status = service.get_next_status(BookingStatus.PENDING)
        assert next_status == BookingStatus.CONFIRMED

    def test_next_status_confirmed_to_in_progress(self):
        service = SchedulingService()
        next_status = service.get_next_status(BookingStatus.CONFIRMED)
        assert next_status == BookingStatus.IN_PROGRESS

    def test_next_status_in_progress_to_completed(self):
        service = SchedulingService()
        next_status = service.get_next_status(BookingStatus.IN_PROGRESS)
        assert next_status == BookingStatus.COMPLETED

    def test_next_status_completed_returns_none(self):
        service = SchedulingService()
        next_status = service.get_next_status(BookingStatus.COMPLETED)
        assert next_status is None

    def test_next_status_cancelled_returns_none(self):
        service = SchedulingService()
        next_status = service.get_next_status(BookingStatus.CANCELLED)
        assert next_status is None

    def test_next_status_rejected_returns_none(self):
        service = SchedulingService()
        next_status = service.get_next_status(BookingStatus.REJECTED)
        assert next_status is None

    def test_state_machine_full_transition_path(self):
        service = SchedulingService()
        current = BookingStatus.PENDING
        path = [current]
        while True:
            next_status = service.get_next_status(current)
            if next_status is None:
                break
            path.append(next_status)
            current = next_status
        assert path == [
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED,
            BookingStatus.IN_PROGRESS,
            BookingStatus.COMPLETED,
        ]
