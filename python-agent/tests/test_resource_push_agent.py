from src.ai_modules.agents.resource_push_agent import ResourcePushAgent


def test_resource_push_agent_skips_json_placeholder_objects() -> None:
    agent = ResourcePushAgent()

    assert not agent._is_pushable_resource(
        {
            "file_name": "thread-pool.json",
            "mime_type": "application/json",
            "object_key": "resources/thread-pool.json",
            "storage_url": "minio://resource-bucket/resources/thread-pool.json",
        }
    )


def test_resource_push_agent_accepts_real_minio_assets() -> None:
    agent = ResourcePushAgent()

    assert agent._is_pushable_resource(
        {
            "file_name": "thread-pool-guide.md",
            "mime_type": "text/markdown",
            "object_key": "resources/thread-pool-guide.md",
            "storage_url": "minio://resource-bucket/resources/thread-pool-guide.md",
        }
    )
