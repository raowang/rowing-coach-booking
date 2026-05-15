from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"


class MemberBase(BaseModel):
    openid: str
    name: str
    phone: Optional[str] = None
    gender: Optional[Gender] = None
    birthday: Optional[date] = None
    membership_start: Optional[date] = None
    membership_end: Optional[date] = None
    skill_level: Optional[SkillLevel] = None
    learning_style: Optional[LearningStyle] = None
    personality_preference: Optional[str] = None
    portrait_data: Optional[dict] = Field(default_factory=dict)


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[Gender] = None
    birthday: Optional[date] = None
    membership_start: Optional[date] = None
    membership_end: Optional[date] = None
    skill_level: Optional[SkillLevel] = None
    learning_style: Optional[LearningStyle] = None
    personality_preference: Optional[str] = None
    portrait_data: Optional[dict] = None


class MemberResponse(MemberBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
