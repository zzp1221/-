from src.ai_modules.llms.agent_models import OpenAICompatibleLearningPathGenerator


def test_learning_path_generator_normalizes_wrapped_payload() -> None:
    generator = OpenAICompatibleLearningPathGenerator.__new__(OpenAICompatibleLearningPathGenerator)

    payload = generator._normalize_learning_plan_payload(
        {
            "learningPath": {
                "goal": "掌握联合索引的最左匹配规则",
                "day": 14,
                "milestone": "完成阶段测试",
                "steps": [
                    {
                        "name": "阶段一",
                        "description": "复习基础概念",
                        "resources": ["联合索引导学文档"],
                        "assessment": "能解释最左匹配含义",
                    }
                ],
                "summary": "14 天学习计划",
            }
        }
    )

    assert payload["goal"] == "掌握联合索引的最左匹配规则"
    assert payload["duration"] == "14天"
    assert payload["milestones"] == ["完成阶段测试"]
    assert payload["summaryText"] == "14 天学习计划"
    assert payload["steps"][0]["title"] == "阶段一"
    assert payload["steps"][0]["objective"] == "复习基础概念"
    assert payload["steps"][0]["activities"] == ["联合索引导学文档"]
    assert payload["steps"][0]["successCriteria"] == "能解释最左匹配含义"


def test_learning_path_generator_uses_milestones_as_steps_when_steps_missing() -> None:
    generator = OpenAICompatibleLearningPathGenerator.__new__(OpenAICompatibleLearningPathGenerator)

    payload = generator._normalize_learning_plan_payload(
        {
            "goal": "掌握联合索引最左匹配",
            "duration": "14天",
            "milestones": [
                {
                    "title": "阶段一",
                    "objective": "理解原理",
                    "activities": ["阅读教材", "整理笔记"],
                    "successCriteria": "能解释最左匹配",
                }
            ],
            "summaryText": "",
        }
    )

    assert payload["milestones"] == ["阶段一"]
    assert payload["steps"][0]["title"] == "阶段一"
    assert payload["steps"][0]["activities"] == ["阅读教材", "整理笔记"]
    assert payload["summaryText"] == "已生成一个 14天 的学习路径，围绕“掌握联合索引最左匹配”推进。"


def test_learning_path_generator_normalizes_activity_dicts_and_derives_milestones() -> None:
    generator = OpenAICompatibleLearningPathGenerator.__new__(OpenAICompatibleLearningPathGenerator)

    payload = generator._normalize_learning_plan_payload(
        {
            "goal": "掌握联合索引最左匹配",
            "duration": "14天",
            "steps": [
                {
                    "name": "阶段 1",
                    "activities": [
                        {"description": "阅读教材"},
                        {"title": "完成练习"},
                    ],
                    "assessment": "能解释原理",
                }
            ],
            "summaryText": "",
        }
    )

    assert payload["milestones"] == ["阶段 1"]
    assert payload["steps"][0]["activities"] == ["阅读教材", "完成练习"]


def test_learning_path_generator_derives_duration_and_summary_from_alternate_fields() -> None:
    generator = OpenAICompatibleLearningPathGenerator.__new__(OpenAICompatibleLearningPathGenerator)

    payload = generator._normalize_learning_plan_payload(
        {
            "target": "掌握联合索引最左匹配",
            "targetPeriod": "14天",
            "steps": [],
            "summaryText": "",
        }
    )

    assert payload["duration"] == "14天"
    assert payload["summaryText"] == "已生成一个 14天 的学习路径，围绕“掌握联合索引最左匹配”推进。"
