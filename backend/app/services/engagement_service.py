import logging
from datetime import date, datetime, timedelta
from typing import Optional

from app.core.directus import get_directus_client

logger = logging.getLogger(__name__)


class EngagementService:
    def __init__(self):
        self.directus = get_directus_client()
        self._sent_cache: set[str] = set()

    def _check_and_mark_sent(self, cache_key: str) -> bool:
        if cache_key in self._sent_cache:
            return False
        self._sent_cache.add(cache_key)
        return True

    async def check_birthday_members(self) -> list[dict]:
        today = date.today()
        try:
            result = await self.directus.query(
                "members",
                filter={
                    "_and": [
                        {"birthday": {"_nnull": True}},
                        {
                            "_or": [
                                {
                                    "membership_end": {
                                        "_lt": (today + timedelta(days=30)).isoformat()
                                    }
                                }
                            ]
                        }
                    ]
                },
                limit=100
            )

            birthday_members = []
            for member in result.get("data", []):
                if member.get("birthday"):
                    birthday = datetime.fromisoformat(member["birthday"]).date()
                    if birthday.month == today.month and birthday.day == today.day:
                        birthday_members.append(member)

            return birthday_members
        except Exception as e:
            logger.error(f"Error checking birthday members: {e}")
            return []

    async def check_renewal_due_members(self, days_threshold: int = 30) -> list[dict]:
        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)
        try:
            result = await self.directus.query(
                "members",
                filter={
                    "membership_end": {
                        "_between": [today.isoformat(), threshold_date.isoformat()]
                    }
                },
                limit=100
            )
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Error checking renewal due members: {e}")
            return []

    async def check_inactive_members(self, days_threshold: int = 14) -> list[dict]:
        threshold_date = datetime.utcnow() - timedelta(days=days_threshold)
        try:
            result = await self.directus.query(
                "members",
                limit=100
            )

            inactive_members = []
            for member in result.get("data", []):
                last_booking = await self._get_last_booking(member["id"])
                if last_booking:
                    completed_at = last_booking.get("completed_at")
                    if completed_at:
                        completed_date = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                        if completed_date < threshold_date:
                            inactive_members.append(member)
                else:
                    created_at = member.get("created_at")
                    if created_at:
                        created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        if created_date < threshold_date:
                            inactive_members.append(member)

            return inactive_members
        except Exception as e:
            logger.error(f"Error checking inactive members: {e}")
            return []

    async def _get_last_booking(self, member_id: str) -> Optional[dict]:
        try:
            result = await self.directus.query(
                "bookings",
                filter={
                    "member_id": {"_eq": member_id},
                    "status": {"_eq": "completed"}
                },
                sort=["-completed_at"],
                limit=1
            )
            data = result.get("data", [])
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Error fetching last booking: {e}")
            return None

    async def send_birthday_message(self, member_id: str) -> bool:
        cache_key = f"birthday_sent:{member_id}:{date.today().isoformat()}"
        if not self._check_and_mark_sent(cache_key):
            return False

        logger.info(f"Birthday message would be sent to member {member_id}")
        return True

    async def send_renewal_reminder(self, member_id: str) -> bool:
        cache_key = f"renewal_reminder:{member_id}"
        if not self._check_and_mark_sent(cache_key):
            return False

        logger.info(f"Renewal reminder would be sent to member {member_id}")
        return True

    async def send_inactivity_reminder(self, member_id: str) -> bool:
        cache_key = f"inactivity_reminder:{member_id}:{date.today().isoformat()}"
        if not self._check_and_mark_sent(cache_key):
            return False

        logger.info(f"Inactivity reminder would be sent to member {member_id}")
        return True

    async def trigger_engagement_checks(self) -> dict:
        results = {
            "birthday_checked": False,
            "renewal_checked": False,
            "inactivity_checked": False,
            "birthday_members_count": 0,
            "renewal_members_count": 0,
            "inactive_members_count": 0
        }

        try:
            birthday_members = await self.check_birthday_members()
            results["birthday_checked"] = True
            results["birthday_members_count"] = len(birthday_members)
            for member in birthday_members:
                await self.send_birthday_message(member["id"])
        except Exception as e:
            logger.error(f"Error in birthday check: {e}")

        try:
            renewal_members = await self.check_renewal_due_members()
            results["renewal_checked"] = True
            results["renewal_members_count"] = len(renewal_members)
            for member in renewal_members:
                await self.send_renewal_reminder(member["id"])
        except Exception as e:
            logger.error(f"Error in renewal check: {e}")

        try:
            inactive_members = await self.check_inactive_members()
            results["inactivity_checked"] = True
            results["inactive_members_count"] = len(inactive_members)
            for member in inactive_members:
                await self.send_inactivity_reminder(member["id"])
        except Exception as e:
            logger.error(f"Error in inactivity check: {e}")

        return results


engagement_service = EngagementService()
