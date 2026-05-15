"""Test member model validation."""
import sys
from datetime import date
from unittest.mock import patch

import pytest

sys.path.insert(0, "/mnt/d/GitHub/ai/agent/reserve-app/rowing-coach-booking/backend")

from app.models.member import (
    Gender,
    LearningStyle,
    MemberBase,
    MemberCreate,
    MemberResponse,
    MemberUpdate,
    SkillLevel,
)


class TestMemberModel:
    def test_member_base_valid(self):
        member = MemberBase(
            openid="test_openid",
            name="Test User",
            phone="13800138000",
            gender=Gender.MALE,
            birthday=date(1990, 5, 15),
            skill_level=SkillLevel.INTERMEDIATE,
        )
        assert member.openid == "test_openid"
        assert member.name == "Test User"
        assert member.gender == Gender.MALE
        assert member.skill_level == SkillLevel.INTERMEDIATE

    def test_member_base_optional_fields(self):
        member = MemberBase(openid="test_openid", name="Minimal User")
        assert member.openid == "test_openid"
        assert member.name == "Minimal User"
        assert member.phone is None
        assert member.gender is None
        assert member.birthday is None
        assert member.skill_level is None

    def test_member_create_valid(self):
        member = MemberCreate(
            openid="wechat_123",
            name="New Member",
            skill_level=SkillLevel.BEGINNER,
        )
        assert member.openid == "wechat_123"
        assert member.skill_level == SkillLevel.BEGINNER

    def test_member_update_partial(self):
        update = MemberUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.phone is None
        assert update.skill_level is None

    def test_member_update_with_all_fields(self):
        update = MemberUpdate(
            name="Updated",
            phone="13900139000",
            gender=Gender.FEMALE,
            skill_level=SkillLevel.ADVANCED,
        )
        assert update.name == "Updated"
        assert update.phone == "13900139000"
        assert update.gender == Gender.FEMALE
        assert update.skill_level == SkillLevel.ADVANCED

    def test_member_response_valid(self):
        response = MemberResponse(
            id="member-123",
            openid="test_openid",
            name="Response User",
            created_at=None,
            updated_at=None,
        )
        assert response.id == "member-123"
        assert response.openid == "test_openid"

    def test_gender_enum_values(self):
        assert Gender.MALE.value == "male"
        assert Gender.FEMALE.value == "female"
        assert Gender.OTHER.value == "other"

    def test_skill_level_enum_values(self):
        assert SkillLevel.BEGINNER.value == "beginner"
        assert SkillLevel.INTERMEDIATE.value == "intermediate"
        assert SkillLevel.ADVANCED.value == "advanced"

    def test_learning_style_enum_values(self):
        assert LearningStyle.VISUAL.value == "visual"
        assert LearningStyle.AUDITORY.value == "auditory"
        assert LearningStyle.KINESTHETIC.value == "kinesthetic"

    def test_member_base_with_portrait_data(self):
        member = MemberBase(
            openid="test",
            name="Portrait User",
            portrait_data={"preferred_specialties": ["technique"]},
        )
        assert member.portrait_data == {"preferred_specialties": ["technique"]}

    def test_member_base_default_portrait_data(self):
        member = MemberBase(openid="test", name="Default Portrait")
        assert member.portrait_data == {}

    def test_member_update_skill_level(self):
        update = MemberUpdate(skill_level=SkillLevel.INTERMEDIATE)
        assert update.skill_level == SkillLevel.INTERMEDIATE

    def test_member_create_with_learning_style(self):
        member = MemberCreate(
            openid="learn_test",
            name="Learning Style User",
            learning_style=LearningStyle.AUDITORY,
        )
        assert member.learning_style == LearningStyle.AUDITORY
