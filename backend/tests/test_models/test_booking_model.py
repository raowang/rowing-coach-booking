"""Test booking model validation."""
import sys
from datetime import datetime
from unittest.mock import patch

import pytest

sys.path.insert(0, "/mnt/d/GitHub/ai/agent/reserve-app/rowing-coach-booking/backend")

from app.models.booking import (
    BookingBase,
    BookingCreate,
    BookingResponse,
    BookingStatus,
    BookingUpdate,
    BookingWithDetails,
)


class TestBookingModel:
    def test_booking_status_enum_values(self):
        assert BookingStatus.PENDING.value == "pending"
        assert BookingStatus.CONFIRMED.value == "confirmed"
        assert BookingStatus.IN_PROGRESS.value == "in_progress"
        assert BookingStatus.COMPLETED.value == "completed"
        assert BookingStatus.CANCELLED.value == "cancelled"
        assert BookingStatus.REJECTED.value == "rejected"

    def test_booking_base_valid(self):
        booking = BookingBase(
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
        )
        assert booking.member_id == "member-123"
        assert booking.coach_id == "coach-456"
        assert booking.status == BookingStatus.PENDING

    def test_booking_base_default_status(self):
        booking = BookingBase(
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
        )
        assert booking.status == BookingStatus.PENDING

    def test_booking_create_valid(self):
        booking = BookingCreate(
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
            status=BookingStatus.PENDING,
        )
        assert booking.member_id == "member-123"
        assert booking.status == BookingStatus.PENDING

    def test_booking_update_partial(self):
        update = BookingUpdate(status=BookingStatus.CONFIRMED)
        assert update.status == BookingStatus.CONFIRMED
        assert update.scheduled_time is None
        assert update.end_time is None

    def test_booking_update_all_fields(self):
        update = BookingUpdate(
            scheduled_time=datetime(2024, 7, 1, 10, 0, 0),
            end_time=datetime(2024, 7, 1, 11, 0, 0),
            status=BookingStatus.CANCELLED,
        )
        assert update.scheduled_time == datetime(2024, 7, 1, 10, 0, 0)
        assert update.end_time == datetime(2024, 7, 1, 11, 0, 0)
        assert update.status == BookingStatus.CANCELLED

    def test_booking_response_valid(self):
        response = BookingResponse(
            id="booking-789",
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
            status=BookingStatus.PENDING,
            created_at=datetime(2024, 5, 15, 0, 0, 0),
            confirmed_at=None,
            completed_at=None,
        )
        assert response.id == "booking-789"
        assert response.status == BookingStatus.PENDING

    def test_booking_response_confirmed(self):
        response = BookingResponse(
            id="booking-790",
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 2, 10, 0, 0),
            end_time=datetime(2024, 6, 2, 11, 0, 0),
            status=BookingStatus.CONFIRMED,
            created_at=datetime(2024, 5, 15, 0, 0, 0),
            confirmed_at=datetime(2024, 5, 16, 0, 0, 0),
            completed_at=None,
        )
        assert response.status == BookingStatus.CONFIRMED
        assert response.confirmed_at is not None
        assert response.completed_at is None

    def test_booking_response_completed(self):
        response = BookingResponse(
            id="booking-791",
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 3, 10, 0, 0),
            end_time=datetime(2024, 6, 3, 11, 0, 0),
            status=BookingStatus.COMPLETED,
            created_at=datetime(2024, 5, 15, 0, 0, 0),
            confirmed_at=datetime(2024, 5, 16, 0, 0, 0),
            completed_at=datetime(2024, 6, 3, 11, 30, 0),
        )
        assert response.status == BookingStatus.COMPLETED
        assert response.completed_at is not None

    def test_booking_with_details_valid(self):
        with_details = BookingWithDetails(
            id="booking-789",
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
            status=BookingStatus.PENDING,
            member_name="Test Member",
            coach_name="Test Coach",
        )
        assert with_details.member_name == "Test Member"
        assert with_details.coach_name == "Test Coach"

    def test_booking_status_transitions(self):
        statuses = [
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED,
            BookingStatus.IN_PROGRESS,
            BookingStatus.COMPLETED,
        ]
        for status in statuses:
            booking = BookingBase(
                member_id="test",
                coach_id="test",
                scheduled_time=datetime.now(),
                end_time=datetime.now(),
                status=status,
            )
            assert booking.status in statuses

    def test_booking_cancelled_status(self):
        booking = BookingBase(
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
            status=BookingStatus.CANCELLED,
        )
        assert booking.status == BookingStatus.CANCELLED

    def test_booking_rejected_status(self):
        booking = BookingBase(
            member_id="member-123",
            coach_id="coach-456",
            scheduled_time=datetime(2024, 6, 1, 10, 0, 0),
            end_time=datetime(2024, 6, 1, 11, 0, 0),
            status=BookingStatus.REJECTED,
        )
        assert booking.status == BookingStatus.REJECTED
