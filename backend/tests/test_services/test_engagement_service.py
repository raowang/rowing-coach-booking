"""Test engagement service for birthday/renewal logic."""
import sys
from datetime import date, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, "/mnt/d/GitHub/ai/agent/reserve-app/rowing-coach-booking/backend")

from app.services.engagement_service import EngagementService


class TestEngagementService:
    @pytest.fixture
    def service_with_mocks(self, mock_directus_client: MagicMock):
        service = EngagementService()
        service.directus = mock_directus_client
        return service

    @pytest.mark.asyncio
    async def test_check_birthday_members_found(
        self,
        service_with_mocks: EngagementService,
    ):
        today = date.today()
        birthday_member = {
            "id": "member-bday",
            "name": "Birthday Member",
            "birthday": f"{today.year}-05-15",
            "membership_end": (today + timedelta(days=30)).isoformat(),
        }
        service_with_mocks.directus.query = AsyncMock(
            return_value={"data": [birthday_member]}
        )
        results = await service_with_mocks.check_birthday_members()
        assert len(results) == 1
        assert results[0]["id"] == "member-bday"

    @pytest.mark.asyncio
    async def test_check_birthday_members_not_today(
        self,
        service_with_mocks: EngagementService,
    ):
        other_member = {
            "id": "member-other",
            "name": "Other Member",
            "birthday": "1990-01-01",
            "membership_end": (date.today() + timedelta(days=30)).isoformat(),
        }
        service_with_mocks.directus.query = AsyncMock(return_value={"data": [other_member]})
        results = await service_with_mocks.check_birthday_members()
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_check_birthday_members_empty_result(
        self,
        service_with_mocks: EngagementService,
    ):
        service_with_mocks.directus.query = AsyncMock(return_value={"data": []})
        results = await service_with_mocks.check_birthday_members()
        assert results == []

    @pytest.mark.asyncio
    async def test_check_renewal_due_members_found(
        self,
        service_with_mocks: EngagementService,
    ):
        today = date.today()
        renewal_member = {
            "id": "member-renewal",
            "name": "Renewal Member",
            "membership_end": (today + timedelta(days=15)).isoformat(),
        }
        service_with_mocks.directus.query = AsyncMock(
            return_value={"data": [renewal_member]}
        )
        results = await service_with_mocks.check_renewal_due_members(days_threshold=30)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_check_renewal_due_members_empty(
        self,
        service_with_mocks: EngagementService,
    ):
        service_with_mocks.directus.query = AsyncMock(return_value={"data": []})
        results = await service_with_mocks.check_renewal_due_members()
        assert results == []

    @pytest.mark.asyncio
    async def test_send_birthday_message_success(
        self,
        service_with_mocks: EngagementService,
    ):
        result = await service_with_mocks.send_birthday_message("member-123")
        assert result is True

    @pytest.mark.asyncio
    async def test_send_birthday_message_already_sent(
        self,
        service_with_mocks: EngagementService,
    ):
        await service_with_mocks.send_birthday_message("member-123")
        result = await service_with_mocks.send_birthday_message("member-123")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_renewal_reminder_success(
        self,
        service_with_mocks: EngagementService,
    ):
        result = await service_with_mocks.send_renewal_reminder("member-123")
        assert result is True

    @pytest.mark.asyncio
    async def test_send_renewal_reminder_already_sent(
        self,
        service_with_mocks: EngagementService,
    ):
        await service_with_mocks.send_renewal_reminder("member-123")
        result = await service_with_mocks.send_renewal_reminder("member-123")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_inactivity_reminder_success(
        self,
        service_with_mocks: EngagementService,
    ):
        result = await service_with_mocks.send_inactivity_reminder("member-123")
        assert result is True

    @pytest.mark.asyncio
    async def test_send_inactivity_reminder_already_sent(
        self,
        service_with_mocks: EngagementService,
    ):
        await service_with_mocks.send_inactivity_reminder("member-123")
        result = await service_with_mocks.send_inactivity_reminder("member-123")
        assert result is False

    @pytest.mark.asyncio
    async def test_trigger_engagement_checks_all_pass(
        self,
        service_with_mocks: EngagementService,
    ):
        service_with_mocks.directus.query = AsyncMock(return_value={"data": []})
        results = await service_with_mocks.trigger_engagement_checks()
        assert results["birthday_checked"] is True
        assert results["renewal_checked"] is True
        assert results["inactivity_checked"] is True
        assert results["birthday_members_count"] == 0
        assert results["renewal_members_count"] == 0
        assert results["inactive_members_count"] == 0

    @pytest.mark.asyncio
    async def test_trigger_engagement_checks_with_members(
        self,
        service_with_mocks: EngagementService,
    ):
        today = date.today()
        birthday_member = {
            "id": "bday-1",
            "name": "Birthday Member",
            "birthday": f"{today.year}-05-15",
            "membership_end": (today + timedelta(days=30)).isoformat(),
        }
        renewal_member = {
            "id": "renewal-1",
            "name": "Renewal Member",
            "membership_end": (today + timedelta(days=15)).isoformat(),
        }
        service_with_mocks.directus.query = AsyncMock(
            side_effect=[
                {"data": [birthday_member]},
                {"data": [renewal_member]},
                {"data": []},
            ]
        )
        results = await service_with_mocks.trigger_engagement_checks()
        assert results["birthday_members_count"] == 1
        assert results["renewal_members_count"] == 1

    @pytest.mark.asyncio
    async def test_get_last_booking_found(
        self,
        service_with_mocks: EngagementService,
        sample_completed_booking_data: dict[str, Any],
    ):
        service_with_mocks.directus.query = AsyncMock(
            return_value={"data": [sample_completed_booking_data]}
        )
        result = await service_with_mocks._get_last_booking("member-123")
        assert result is not None
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_last_booking_not_found(
        self,
        service_with_mocks: EngagementService,
    ):
        service_with_mocks.directus.query = AsyncMock(return_value={"data": []})
        result = await service_with_mocks._get_last_booking("member-123")
        assert result is None