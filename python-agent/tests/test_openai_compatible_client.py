from src.ai_modules.llms.openai_compatible import extract_json_object_from_text


def test_extract_json_object_from_text_prefers_fenced_final_object() -> None:
    mixed_output = """
推理草稿:
{"topic":"联合索引","attempt":1}

最终答案:
```json
{"title":"联合索引导学","summary":"真实结构化输出"}
```
"""

    payload = extract_json_object_from_text(mixed_output)

    assert payload["title"] == "联合索引导学"
    assert payload["summary"] == "真实结构化输出"


def test_extract_json_object_from_text_prefers_outermost_object_for_plain_json() -> None:
    mixed_output = """
{
  "title": "联合索引导学",
  "slides": [
    {
      "title": "第一页",
      "bullets": ["A", "B"]
    }
  ]
}
"""

    payload = extract_json_object_from_text(mixed_output)

    assert payload["title"] == "联合索引导学"
    assert isinstance(payload["slides"], list)
