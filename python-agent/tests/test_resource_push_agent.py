from src.ai_modules.agents.resource_push_agent import ResourcePushAgent


def test_resource_push_agent_only_accepts_http_direct_urls() -> None:
    agent = ResourcePushAgent()

    assert agent._is_http_url("https://example.com/file.md")
    assert not agent._is_http_url("custom://resource-bucket/resources/thread-pool-guide.md")


def test_resource_push_agent_builds_query_from_profile_context() -> None:
    agent = ResourcePushAgent()

    query = agent._build_query(
        {"resourceType": "CODE_CASE"},
        {
            "primaryWeakPoint": "线程池参数调优",
            "currentCourse": "Java 程序设计",
            "currentChapter": "并发编程",
            "studentLevel": "INTERMEDIATE",
        },
    )

    assert query == "线程池参数调优 / Java 程序设计 / 并发编程 / INTERMEDIATE / 代码案例"


def test_resource_push_agent_filters_non_video_pages() -> None:
    agent = ResourcePushAgent()

    assert not agent._is_valid_video_result({}, "https://example.com/paper.pdf", "并发编程论文")
    assert not agent._is_valid_video_result({}, "https://github.com/example/repo", "示例仓库")
    assert agent._is_valid_video_result({}, "https://www.bilibili.com/video/BV1xx", "并发编程视频讲解")
