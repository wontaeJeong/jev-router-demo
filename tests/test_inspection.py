import json

import pytest

from jev_router_demo.inspection import abbreviate, export_result, inspect_result
from jev_router_demo.models import HttpExchange, RoutingResult


def test_abbreviation_preserves_structure_and_original():
    original = {"messages": [{"content": "가" * 600}], "stream": False, "n": 0, "empty": None}
    preview, count = abbreviate(original)
    assert original["messages"][0]["content"] == "가" * 600
    assert preview["messages"][0]["content"] == "가" * 320 + "… [중략: 160자] …" + "가" * 120
    assert (preview["stream"], preview["n"], preview["empty"], count) == (False, 0, None, 1)


@pytest.mark.parametrize("size,count", [(0, 0), (480, 0), (481, 1)])
def test_abbreviation_boundary(size, count):
    preview, found = abbreviate("x" * size)
    assert found == count
    if not count:
        assert preview == "x" * size


def test_inspect_and_export_original_without_overwrite(tmp_path):
    result = RoutingResult("LLM", http=HttpExchange("POST", "http://llm", {"prompt": "원본" * 600}))
    assert "중략" in inspect_result(result, "request")
    assert json.loads(inspect_result(result, "request", full=True))["prompt"] == "원본" * 600
    first = export_result(result, "request", tmp_path)
    second = export_result(result, "request", tmp_path)
    assert first != second
    assert json.loads(first.read_text())["prompt"] == "원본" * 600


def test_raw_text_keeps_whitespace():
    result = RoutingResult("LLM", http=HttpExchange("POST", "http://llm", {}, response_text=' {"x": 1} \n'))
    assert inspect_result(result, "raw", full=True) == ' {"x": 1} \n'
