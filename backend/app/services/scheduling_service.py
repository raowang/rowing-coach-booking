import logging
from datetime import datetime, timedelta
from typing import Optional

from app.core.directus import get_directus_client
from app.models import BookingStatus, BookingResponse

logger = logging.getLogger(__name__)


class SchedulingService:
    def __init__(self):
        self.directus = get_directus_client()

    async def check_availability(
        self,
        coach_id: str,
        scheduled_time: datetime,
        end_time: datetime
    ) -> bool:
        try:
            result = await self.directus.query(
                "bookings",
                filter={
                    "coach_id": {"_eq": coach_id},
                    "status": {"_in": [
                        BookingStatus.PENDING.value,
                        BookingStatus.CONFIRMED.value,
                        BookingStatus.IN_PROGRESS.value
                    ]},
                    "_or": [
                        {
                            "scheduled_time": {"_lte": scheduled_time.isoformat()},
                            "end_time": {"_gt": scheduled_time.isoformat()}
                        },
                        {
                            "scheduled_time": {"_lt": end_time.isoformat()},
                            "end_time": {"_gte": end_time.isoformat()}
                        },
                        {
                            "scheduled_time": {"_gte": scheduled_time.isoformat()},
                            "end_time": {"_lte": end_time.isoformat()}
                        }
                    ]
                },
                limit=1
            )
            return len(result.get("data", [])) == 0
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return False

    async def create_booking(
        self,
        member_id: str,
        coach_id: str,
        scheduled_time: datetime,
        end_time: datetime
    ) -> Optional[dict]:
        if not await self.check_availability(coach_id, scheduled_time, end_time):
            return None

        try:
            result = await self.directus.create_item("bookings", {
                "member_id": member_id,
                "coach_id": coach_id,
                "scheduled_time": scheduled_time.isoformat(),
                "end_time": end_time.isoformat(),
                "status": BookingStatus.PENDING.value
            })
            return result.get("data")
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return None

    async def confirm_booking(self, booking_id: str) -> Optional[dict]:
        try:
            result = await self.directus.update_item("bookings", booking_id, {
                "status": BookingStatus.CONFIRMED.value,
                "confirmed_at": datetime.utcnow().isoformat()
            })
            return result.get("data")
        except Exception as e:
            logger.error(f"Error confirming booking: {e}")
            return None

    async def reject_booking(self, booking_id: str, reason: Optional[str] = None) -> Optional[dict]:
        try:
            update_data = {
                "status": BookingStatus.REJECTED.value
            }
            if reason:
                update_data["rejection_reason"] = reason

            result = await self.directus.update_item("bookings", booking_id, update_data)
            return result.get("data")
        except Exception as e:
            logger.error(f"Error rejecting booking: {e}")
            return None

    async def cancel_booking(self, booking_id: str) -> Optional[dict]:
        try:
            result = await self.directus.update_item("bookings", booking_id, {
                "status": BookingStatus.CANCELLED.value
            })
            return result.get("data")
        except Exception as e:
            logger.error(f"Error cancelling booking: {e}")
            return None

    async def start_training(self, booking_id: str) -> Optional[dict]:
        try:
            result = await self.directus.update_item("bookings", booking_id, {
                "status": BookingStatus.IN_PROGRESS.value
            })
            return result.get("data")
        except Exception as e:
            logger.error(f"Error starting training: {e}")
            return None

    async def complete_training(self, booking_id: str) -> Optional[dict]:
        try:
            result = await self.directus.update_item("bookings", booking_id, {
                "status": BookingStatus.COMPLETED.value,
                "completed_at": datetime.utcnow().isoformat()
            })
            return result.get("data")
        except Exception as e:
            logger.error(f"Error completing training: {e}")
            return None

    async def get_booking(self, booking_id: str) -> Optional[dict]:
        try:
            result = await self.directus.get_item("bookings", booking_id)
            return result.get("data")
        except Exception as e:
            logger.error(f"Error fetching booking: {e}")
            return None

    async def get_pending_bookings(
        self,
        coach_id: Optional[str] = None,
        limit: int = 50
    ) -> list[dict]:
        try:
            filter_cond = {"status": {"_eq": BookingStatus.PENDING.value}}
            if coach_id:
                filter_cond["coach_id"] = {"_eq": coach_id}

            result = await self.directus.query(
                "bookings",
                filter=filter_cond,
                sort=["scheduled_time"],
                limit=limit
            )
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Error fetching pending bookings: {e}")
            return []

    def get_next_status(self, current_status: BookingStatus) -> Optional[BookingStatus]:
        transitions = {
            BookingStatus.PENDING: BookingStatus.CONFIRMED,
            BookingStatus.CONFIRMED: BookingStatus.IN_PROGRESS,
            BookingStatus.IN_PROGRESS: BookingStatus.COMPLETED,
        }
        return transitions.get(current_status)


scheduling_service = SchedulingService()
