from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TeachingStyle(str, Enum):
    PATIENT = "patient"
    PROFESSIONAL = "professional"
    STRICT = "strict"


class CoachBase(BaseModel):
    name: str
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    teaching_style: Optional[TeachingStyle] = None
    specialties: list[str] = Field(default_factory=list)
    rating: float = 5.0
    review_count: int = 0
    is_active: bool = True


class CoachCreate(CoachBase):
    pass


class CoachUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    teaching_style: Optional[TeachingStyle] = None
    specialties: Optional[list[str]] = None
    is_active: Optional[bool] = None


class CoachResponse(CoachBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
