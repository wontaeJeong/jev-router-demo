import asyncio
import json

import httpx
import pytest

from jev_router_demo.config import Config
from jev_router_demo.routers.systemone import SystemOneRouter, parse_systemone_response
from jev_router_demo.session import DemoSession
from test_routers import llm_response


def typed_response():
    return {"model": "typesafe/jev-1.13", "answers": {
        "model_tier": {"type": "choice", "choice": "reasoning", "probabilities": {"fast": 0.02, "standard": 0.08, "reasoning": 0.9}},
        "needs_web": {"type": "choice", "choice": "true", "probabilities": {"true": 0.8, "false": 0.2}},
        "needs_approval": {"type": "choice", "choice": "false"},
    }, "usage": {"input_tokens": 476, "output_tokens": 70, "cost": 0.000019992}}


@pytest.mark.parametrize("endpoint", ["https://openrouter.ai/api/v1/systemone", "https://openrouter.ai/api/alpha/decisions", "http://local/v1/systemone"])
def test_typed_api_uses_exact_endpoint_and_original_state(endpoint):
    async def check():
        config = Config("http://llm/v1", "baseline", "", "typesafe/jev-1.13", jev_api_mode="systemone", jev_endpoint_url=endpoint, jev_api_key="jev-secret")
        original = "원본 요청\n" * 500
        def handler(request):
            assert str(request.url) == endpoint
            body = json.loads(request.content)
            assert body["state"] == original
            assert set(body) == {"model", "state", "questions"}
            assert body["questions"]["model_tier"]["type"] == "choice"
            assert set(body["questions"]["needs_web"]["criteria"]) == {"true", "false"}
            assert request.headers["authorization"] == "Bearer jev-secret"
            return httpx.Response(200, json=typed_response())
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await SystemOneRouter(client, config).route(original)
        assert result.decision.model_tier == "reasoning"
        assert result.decision.needs_web is True and result.decision.needs_approval is False
        assert result.output_kind == "typed" and result.parse_required is False
        assert result.parse_success is None and result.parse_ms is None
        assert result.generated_text is None and result.generated_bytes is None
        assert (result.input_tokens, result.output_tokens, result.total_tokens) == (476, 70, 546)
        assert result.probabilities["model_tier"]["reasoning"] == 0.9
        assert result.http.request_body["state"] == original
    asyncio.run(check())


@pytest.mark.parametrize("invalid", ["missing", "type", "label", "boolean", "probability"])
def test_invalid_typed_answer_is_not_guessed(invalid):
    payload = typed_response()
    if invalid == "missing":
        del payload["answers"]["needs_approval"]
    elif invalid == "type":
        payload["answers"]["needs_web"] = {"type": "noul", "noul": 0.8}
    elif invalid == "label":
        payload["answers"]["model_tier"]["choice"] = "super-smart"
    elif invalid == "boolean":
        payload["answers"]["needs_web"]["choice"] = True
    else:
        payload["answers"]["model_tier"]["probabilities"]["reasoning"] = float("nan")
    result = parse_systemone_response(payload)
    assert result.error and result.decision is None
    assert result.output_tokens == 70
    assert result.parse_success is None


def test_typed_usage_missing_is_not_zero():
    payload = typed_response()
    del payload["usage"]
    result = parse_systemone_response(payload)
    assert result.decision
    assert result.input_tokens is None and result.output_tokens is None and result.total_tokens is None


@pytest.mark.parametrize("mode", ["systemone", "ollama"])
def test_session_selects_typed_adapter_and_auth_is_separate(mode):
    async def check():
        config = Config("http://llm/v1", "baseline", "http://jev", "jev-1.13", "llm-secret", jev_api_mode=mode, jev_api_key="jev-secret")
        def handler(request):
            if request.url.host == "llm":
                assert request.headers["authorization"] == "Bearer llm-secret"
                return httpx.Response(200, json=llm_response())
            assert request.url.path == "/v1/systemone"
            assert request.headers["authorization"] == "Bearer jev-secret"
            return httpx.Response(200, json=typed_response())
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            session = DemoSession(config, client)
            events = [event async for event in session.run("request")]
            result = events[-1]["snapshot"]["results"]["JEV"]
            assert result["output_kind"] == "typed"
            assert events[-1]["snapshot"]["metrics"]["JEV"]["parse_attempts"] == 0
            assert "jev-secret" not in json.dumps(events)
    asyncio.run(check())


@pytest.mark.parametrize("mode,path", [("systemone", "/v1/systemone"), ("decisions", "/alpha/decisions")])
def test_typed_http_errors_keep_kind_and_request(mode, path):
    async def check():
        config = Config("http://llm", "baseline", "https://openrouter.ai/api", "typesafe/jev-1.13", jev_api_mode=mode, jev_api_key="key")
        def handler(request):
            assert request.url.path == "/api" + path
            return httpx.Response(401, json={"error": {"message": "Invalid key"}})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await SystemOneRouter(client, config).route("request")
        assert result.error and result.output_kind == "typed" and not result.parse_required
        assert result.http.response_json == {"error": {"message": "Invalid key"}}
    asyncio.run(check())


def test_huge_probability_is_validation_error_and_other_backend_finishes():
    async def check():
        config = Config("http://llm/v1", "baseline", "http://jev", "jev-1.13", jev_api_mode="systemone")
        async def handler(request):
            if request.url.host == "llm":
                await asyncio.sleep(0.02)
                return httpx.Response(200, json=llm_response())
            payload = typed_response()
            payload["answers"]["model_tier"]["probabilities"]["fast"] = 10 ** 400
            return httpx.Response(200, json=payload)
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            session = DemoSession(config, client)
            events = [event async for event in session.run("request")]
            assert events[-1]["type"] == "finished"
            assert session.states == {"LLM": "success", "JEV": "error"}
            assert session.results["JEV"].output_tokens == 70
            assert session.results["JEV"].http.response_json["answers"]["model_tier"]["probabilities"]["fast"] == 10 ** 400
            assert session.metrics["LLM"].successes == 1
    asyncio.run(check())
