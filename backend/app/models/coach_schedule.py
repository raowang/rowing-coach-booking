from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel


class CoachScheduleBase(BaseModel):
    coach_id: str
    date: date
    start_time: time
    end_time: time
    is_available: bool = True
    booking_id: Optional[str] = None


class CoachScheduleCreate(CoachScheduleBase):
    pass


class CoachScheduleUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None
    booking_id: Optional[str] = None


class CoachScheduleResponse(CoachScheduleBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CoachScheduleWithCoach(CoachScheduleResponse):
    coach_name: Optional[str] = None
