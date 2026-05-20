from src.ai_modules.retrieval.query_classifier import QueryClassifier


def test_query_classifier_routes_small_talk_without_retrieval() -> None:
    result = QueryClassifier().classify({"query": "你好"})

    assert result.query_type == "SMALL_TALK"
    assert result.retrieval_strategy == "NONE"


def test_query_classifier_routes_answer_previous_from_dialogue_state() -> None:
    result = QueryClassifier().classify(
        {
            "query": "我选 A",
            "messages": [
                {"role": "assistant", "content": "这道题你觉得答案是什么？"},
                {"role": "user", "content": "我选 A"},
            ],
        }
    )

    assert result.query_type == "ANSWER_PREVIOUS"
    assert result.retrieval_strategy == "CONTEXT_ONLY"


def test_query_classifier_routes_new_concept_to_local_hybrid() -> None:
    result = QueryClassifier().classify({"query": "Java volatile 是什么"})

    assert result.query_type == "NEW_CONCEPT"
    assert result.retrieval_strategy == "LOCAL_HYBRID"


def test_query_classifier_routes_error_debug_to_local_hybrid() -> None:
    result = QueryClassifier().classify({"query": "NullPointerException 报错怎么办"})

    assert result.query_type == "ERROR_DEBUG"
    assert result.retrieval_strategy == "LOCAL_HYBRID"


def test_query_classifier_routes_current_info_to_web_augmented() -> None:
    result = QueryClassifier().classify({"query": "今天最新版本有什么变化"})

    assert result.query_type == "CURRENT_INFO"
    assert result.retrieval_strategy == "WEB_AUGMENTED"


def test_query_classifier_routes_image_question() -> None:
    result = QueryClassifier().classify({"query": "看图讲一下这道题", "imageUrls": ["mock://image.png"]})

    assert result.query_type == "IMAGE_QUESTION"
    assert result.retrieval_strategy == "LOCAL_HYBRID"


def test_query_classifier_routes_deep_reasoning() -> None:
    result = QueryClassifier().classify({"query": "分析所有边界", "reasoningMode": "DEEP"})

    assert result.query_type == "DEEP_REASONING"
    assert result.retrieval_strategy == "DEEP_EVIDENCE"
