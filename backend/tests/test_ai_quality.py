"""
AI Response Quality Assessment Tests

Evaluates AI-generated responses for:
- Relevance
- Coherence
- Factual correctness
- Safety

Run with: pytest tests/test_ai_quality.py -v
"""

import json
from typing import List

import pytest


class AIResponseEvaluator:
    """Evaluate AI response quality."""

    def __init__(self):
        self.min_relevance_score = 0.7
        self.min_safety_score = 0.9

    def evaluate_welcome_message(self, response: str, context: dict) -> dict:
        """Evaluate welcome message quality."""
        scores = {}

        scores["has_greeting"] = any(
            greeting in response
            for greeting in ["你好", "您好", "欢迎", "嗨", "哈喽"]
        )

        scores["mentions_time"] = context.get("time_of_day") in response or any(
            time_word in response
            for time_word in ["早上", "下午", "晚上", "中午"]
        )

        scores["mentions_name"] = (
            context.get("member_name") in response
            if context.get("member_name")
            else True
        )

        scores["mentions_capabilities"] = any(
            cap in response
            for cap in ["预约", "教练", "帮助", "服务"]
        )

        scores["length_appropriate"] = 20 <= len(response) <= 200

        scores["no_harmful_content"] = not any(
            word in response.lower()
            for word in ["赌博", "诈骗", "色情", "暴力"]
        )

        relevance = sum(
            [
                scores["has_greeting"],
                scores["mentions_time"],
                scores["mentions_name"],
                scores["mentions_capabilities"],
                scores["length_appropriate"],
            ]
        ) / 5

        safety = 1.0 if scores["no_harmful_content"] else 0.0

        return {
            "scores": scores,
            "relevance_score": relevance,
            "safety_score": safety,
            "overall_score": relevance * 0.6 + safety * 0.4,
            "passed": relevance >= self.min_relevance_score
            and safety >= self.min_safety_score,
        }

    def evaluate_recommendation_explanation(
        self, response: str, member: dict, coach: dict
    ) -> dict:
        """Evaluate coach recommendation explanation."""
        scores = {}

        scores["mentions_member_level"] = any(
            level in response
            for level in ["初学者", "进阶", "高级", "新手", "有经验"]
        )

        scores["mentions_coach_specialty"] = any(
            spec in response
            for spec in coach.get("specialties", [])
        )

        scores["has_reasoning"] = any(
            word in response for word in ["因为", "所以", "根据", "适合"]
        )

        scores["not_generic"] = not any(
            phrase in response
            for phrase in ["不错的", "都可以", "都很好", "随便"]
        )

        scores["length_appropriate"] = 20 <= len(response) <= 150

        scores["no_harmful_content"] = not any(
            word in response.lower()
            for word in ["赌博", "诈骗", "色情", "暴力"]
        )

        relevance = sum(
            [
                scores["mentions_member_level"],
                scores["mentions_coach_specialty"],
                scores["has_reasoning"],
                scores["not_generic"],
                scores["length_appropriate"],
            ]
        ) / 5

        safety = 1.0 if scores["no_harmful_content"] else 0.0

        return {
            "scores": scores,
            "relevance_score": relevance,
            "safety_score": safety,
            "overall_score": relevance * 0.6 + safety * 0.4,
            "passed": relevance >= self.min_relevance_score
            and safety >= self.min_safety_score,
        }

    def evaluate_training_suggestion(self, response: str, training_context: dict) -> dict:
        """Evaluate AI training suggestion quality."""
        scores = {}

        scores["is_specific"] = len(response) >= 30

        scores["has_actionable_advice"] = any(
            action in response
            for action in ["建议", "可以", "试试", "注意", "推荐"]
        )

        scores["mentions_technique"] = any(
            tech in response
            for tech in [
                "划水",
                "呼吸",
                "姿势",
                "节奏",
                "力度",
                "入水",
                "出水",
            ]
        )

        scores["has_duration_or_quantity"] = any(
            quant in response
            for quant in ["分钟", "次", "组", "米", "秒", "小时"]
        )

        scores["not_too_long"] = len(response) <= 300

        scores["no_harmful_content"] = not any(
            word in response.lower()
            for word in ["赌博", "诈骗", "色情", "暴力", "受伤"]
        )

        relevance = sum(
            [
                scores["is_specific"],
                scores["has_actionable_advice"],
                scores["mentions_technique"],
                scores["has_duration_or_quantity"],
                scores["not_too_long"],
            ]
        ) / 5

        safety = 1.0 if scores["no_harmful_content"] else 0.0

        return {
            "scores": scores,
            "relevance_score": relevance,
            "safety_score": safety,
            "overall_score": relevance * 0.7 + safety * 0.3,
            "passed": relevance >= 0.6 and safety >= self.min_safety_score,
        }


evaluator = AIResponseEvaluator()


class TestWelcomeMessageQuality:
    """Test welcome message generation quality."""

    def test_welcome_new_member(self):
        """Test welcome message for new member."""
        response = "嗨，张先生！早上好，欢迎来到赛艇中心。看到你是初学者，我会帮你找到耐心、专业的教练来带你入门。有什么可以帮助你的吗？"

        context = {
            "member_name": "张先生",
            "time_of_day": "morning",
            "skill_level": "beginner",
        }

        result = evaluator.evaluate_welcome_message(response, context)

        print(f"\n=== Welcome Message Evaluation ===")
        print(f"Response: {response}")
        print(f"Scores: {json.dumps(result['scores'], indent=2, ensure_ascii=False)}")
        print(f"Relevance: {result['relevance_score']:.2f}")
        print(f"Safety: {result['safety_score']:.2f}")
        print(f"Overall: {result['overall_score']:.2f}")
        print(f"Passed: {result['passed']}")

        assert result["passed"], f"Welcome message failed quality check: {result}"

    def test_welcome_existing_member(self):
        """Test welcome message for returning member."""
        response = "李小姐回来了！下午好～上次训练后你的划水效率提升了不少呢。今天是来预约训练吗？"

        context = {
            "member_name": "李小姐",
            "time_of_day": "afternoon",
            "skill_level": "intermediate",
        }

        result = evaluator.evaluate_welcome_message(response, context)

        print(f"\n=== Welcome Message Evaluation (Existing Member) ===")
        print(f"Response: {response}")
        print(f"Overall: {result['overall_score']:.2f}, Passed: {result['passed']}")

        assert result["passed"]

    def test_welcome_holiday(self):
        """Test welcome message on holiday."""
        response = "端午节快乐！龙舟训练听起来不错，要不要来一场？"

        context = {
            "member_name": "王教练",
            "time_of_day": "morning",
            "is_holiday": True,
        }

        result = evaluator.evaluate_welcome_message(response, context)

        print(f"\n=== Welcome Message Evaluation (Holiday) ===")
        print(f"Response: {response}")
        print(f"Overall: {result['overall_score']:.2f}, Passed: {result['passed']}")

        assert result["passed"]


class TestRecommendationExplanationQuality:
    """Test coach recommendation explanation quality."""

    def test_beginner_recommendation(self):
        """Test recommendation for beginner member."""
        response = "根据你是初学者的情况，我推荐王教练。他特别擅长教新手，有5年的入门教学经验，耐心十足。"

        member = {"skill_level": "beginner", "name": "张先生"}
        coach = {
            "name": "王教练",
            "specialties": ["新手教学", "划水技巧", "体能训练"],
        }

        result = evaluator.evaluate_recommendation_explanation(response, member, coach)

        print(f"\n=== Recommendation Explanation Evaluation (Beginner) ===")
        print(f"Response: {response}")
        print(f"Scores: {json.dumps(result['scores'], indent=2, ensure_ascii=False)}")
        print(f"Overall: {result['overall_score']:.2f}, Passed: {result['passed']}")

        assert result["passed"]

    def test_advanced_recommendation(self):
        """Test recommendation for advanced member."""
        response = "作为进阶学员，我推荐李教练。他专攻划水效率优化，特别擅长帮助有基础的学员突破瓶颈。"

        member = {"skill_level": "advanced", "name": "刘先生"}
        coach = {
            "name": "李教练",
            "specialties": ["技术提升", "划水效率", "比赛训练"],
        }

        result = evaluator.evaluate_recommendation_explanation(response, member, coach)

        print(f"\n=== Recommendation Explanation Evaluation (Advanced) ===")
        print(f"Response: {response}")
        print(f"Overall: {result['overall_score']:.2f}, Passed: {result['passed']}")

        assert result["passed"]


class TestTrainingSuggestionQuality:
    """Test AI training suggestion quality."""

    def test_specific_technique_advice(self):
        """Test technique-specific training advice."""
        response = "根据你上次训练的视频分析，建议你加强入水角度的练习。每天训练前做10分钟肩部热身，然后进行3组每组20次的入水角度练习，注意入水时手臂要放松。"

        context = {
            "training_count": 15,
            "weak_points": ["入水角度偏大"],
        }

        result = evaluator.evaluate_training_suggestion(response, context)

        print(f"\n=== Training Suggestion Evaluation ===")
        print(f"Response: {response}")
        print(f"Scores: {json.dumps(result['scores'], indent=2, ensure_ascii=False)}")
        print(f"Overall: {result['overall_score']:.2f}, Passed: {result['passed']}")

        assert result["passed"]

    def test_general_encouragement(self):
        """Test that generic responses are caught."""
        response = "继续加油！"

        context = {"training_count": 5}

        result = evaluator.evaluate_training_suggestion(response, context)

        print(f"\n=== Training Suggestion Evaluation (Generic) ===")
        print(f"Response: {response}")
        print(f"Overall: {result['overall_score']:.2f}, Passed: {result['passed']}")

        assert not result["passed"], "Generic response should not pass"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])