import json

import pytest

from jev_router_demo.models import parse_decision


DECISION = {"model_tier": "fast", "needs_web": False, "needs_approval": False}


@pytest.mark.parametrize("fenced", [False, True])
def test_json_and_fenced_json(fenced):
    text = json.dumps(DECISION)
    if fenced:
        text = f"```json\n{text}\n```"
    decision = parse_decision(text)
    assert decision.model_tier == "fast"
    assert decision.needs_web is False
    assert decision.needs_approval is False


@pytest.mark.parametrize(
    "update",
    [{"model_tier": "super-smart"}, {"needs_web": "false"}, {"extra": 1}],
)
def test_invalid_values_fail(update):
    with pytest.raises(ValueError):
        parse_decision(json.dumps(DECISION | update))


def test_invalid_json_fails():
    with pytest.raises(ValueError):
        parse_decision("not json")
