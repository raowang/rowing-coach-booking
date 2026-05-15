from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TrainingRecordBase(BaseModel):
    booking_id: str
    member_id: str
    coach_id: str
    rating: int = Field(ge=1, le=5)
    coach_comment: Optional[str] = None
    ai_suggestions: dict = Field(default_factory=dict)


class TrainingRecordCreate(TrainingRecordBase):
    pass


class TrainingRecordUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    coach_comment: Optional[str] = None
    ai_suggestions: Optional[dict] = None


class TrainingRecordResponse(TrainingRecordBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
