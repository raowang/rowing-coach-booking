from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class BookingBase(BaseModel):
    member_id: str
    coach_id: str
    scheduled_time: datetime
    end_time: datetime
    status: BookingStatus = BookingStatus.PENDING


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None


class BookingResponse(BookingBase):
    id: str
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookingWithDetails(BookingResponse):
    member_name: Optional[str] = None
    coach_name: Optional[str] = None
