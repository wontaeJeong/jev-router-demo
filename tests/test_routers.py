import asyncio
import json

import httpx
import pytest

from jev_router_demo.config import Config
from jev_router_demo.main import compare
from jev_router_demo.routers.litellm import LiteLLMRouter, parse_llm_response
from jev_router_demo.routers.factory import create_jev_router
from jev_router_demo.routers.systemone import parse_systemone_response


DECISION = {"model_tier": "reasoning", "needs_web": True, "needs_approval": False}
TEXT = json.dumps(DECISION)
CONFIG = Config("http://llm/v1", "baseline", "http://jev", "jev-like")


def llm_response(text=TEXT):
    return {"choices": [{"message": {"content": text}}], "usage": {
        "prompt_tokens": 12, "completion_tokens": 5, "total_tokens": 17,
    }}


def jev_response():
    return {"model": "jev-like", "answers": {
        "model_tier": {"type": "choice", "choice": "reasoning"},
        "needs_web": {"type": "choice", "choice": "true"},
        "needs_approval": {"type": "choice", "choice": "false"},
    }, "usage": {"input_tokens": 9, "output_tokens": 4}}


def run_pair(handler, config=CONFIG, request="Full original request\nwith another line."):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await compare(request, LiteLLMRouter(client, config), create_jev_router(client, config))
    return asyncio.run(run())


def test_concurrent_calls_preserve_full_request_and_real_usage():
    async def run():
        entered = 0
        both_started = asyncio.Event()
        original = "Do not modify production.\nInspect recent regressions."

        async def handler(request):
            nonlocal entered
            body = json.loads(request.content)
            entered += 1
            if entered == 2:
                both_started.set()
            await asyncio.wait_for(both_started.wait(), timeout=1)
            if request.url.host == "llm":
                assert request.url.path == "/v1/chat/completions"
                assert body["messages"][1]["content"] == original
                assert "authorization" not in request.headers
                return httpx.Response(200, json=llm_response())
            assert request.url.path == "/v1/systemone"
            assert body["state"] == original
            assert set(body) == {"model", "state", "questions"}
            assert "authorization" not in request.headers
            return httpx.Response(200, json=jev_response())

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            llm, jev = await compare(original, LiteLLMRouter(client, CONFIG), create_jev_router(client, CONFIG))
        assert llm.decision == jev.decision
        assert (llm.input_tokens, llm.output_tokens, llm.total_tokens) == (12, 5, 17)
        assert (jev.input_tokens, jev.output_tokens, jev.total_tokens) == (9, 4, 13)
        assert llm.latency_ms >= llm.parse_ms >= 0
        assert llm.parse_required and llm.parse_success
        assert llm.generated_bytes == len(TEXT.encode())
        assert llm.output_kind == "generated"
        assert jev.latency_ms >= 0
        assert not jev.parse_required and jev.parse_success is None
        assert jev.parse_ms is None and jev.generated_bytes is None
        assert jev.output_kind == "typed"
        assert jev.probabilities is None
    asyncio.run(run())


def test_api_key_is_sent_only_to_litellm():
    config = Config("http://llm/v1", "baseline", "http://jev", "jev", "secret")

    def handler(request):
        if request.url.host == "llm":
            assert request.headers["authorization"] == "Bearer secret"
            return httpx.Response(200, json=llm_response())
        assert "authorization" not in request.headers
        return httpx.Response(200, json=jev_response())
    run_pair(handler, config)


@pytest.mark.parametrize("failure", ["connection", "timeout", "http", "json", "envelope", "parse"])
def test_one_backend_failure_keeps_other_result(failure):
    def handler(request):
        if request.url.host == "jev":
            return httpx.Response(200, json=jev_response())
        if failure == "connection":
            raise httpx.ConnectError("connection refused", request=request)
        if failure == "timeout":
            raise httpx.ReadTimeout("timed out", request=request)
        if failure == "http":
            return httpx.Response(404, json={"error": {"message": "Model missing"}})
        if failure == "json":
            return httpx.Response(200, text="not JSON")
        if failure == "envelope":
            return httpx.Response(200, json={"choices": []})
        return httpx.Response(200, json=llm_response("not a routing result"))

    llm, jev = run_pair(handler)
    assert llm.error
    assert llm.decision is None
    assert jev.decision.model_tier == "reasoning"
    assert jev.error is None
    assert llm.latency_ms >= 0
    if failure == "parse":
        assert llm.parse_success is False
        assert llm.output_tokens == 5
        assert llm.generated_text == "not a routing result"
    else:
        assert llm.parse_success is None


@pytest.mark.parametrize("payload", [[], {}, {"answers": 5}, {"error": "model not found"}, {"response": TEXT, "done": True}])
def test_jev_unexpected_response_is_visible(payload):
    def handler(request):
        return httpx.Response(200, json=payload if request.url.host == "jev" else llm_response())
    llm, jev = run_pair(handler)
    assert llm.decision
    assert jev.error


def test_jev_invalid_decision_retains_typed_usage():
    payload = jev_response()
    payload["answers"]["model_tier"]["choice"] = "super-smart"
    result = parse_systemone_response(payload)
    assert result.parse_success is None
    assert result.error
    assert result.output_tokens == 4
    assert result.generated_text is None


def test_missing_usage_is_not_zero_and_thinking_bytes_are_counted():
    payload = llm_response()
    del payload["usage"]
    payload["choices"][0]["message"]["reasoning_content"] = "분석"
    result = parse_llm_response(payload)
    assert result.input_tokens is None
    assert result.output_tokens is None
    assert result.total_tokens is None
    assert result.generated_bytes == len((TEXT + "분석").encode("utf-8"))
    assert result.thinking_text == "분석"


def test_zero_usage_is_preserved():
    result = parse_systemone_response(jev_response() | {"usage": {"input_tokens": 9, "output_tokens": 0}})
    assert result.output_tokens == 0


@pytest.mark.parametrize("field", ["content", "reasoning_content"])
def test_invalid_generated_unicode_does_not_discard_other_backend(field):
    def handler(request):
        payload = llm_response() if request.url.host == "llm" else jev_response()
        if request.url.host == "llm":
            payload["choices"][0]["message"][field] = "\ud800"
        return httpx.Response(200, content=json.dumps(payload).encode("ascii"))
    llm, jev = run_pair(handler)
    assert "Unicode" in llm.error
    assert llm.generated_bytes is None
    assert jev.decision


def test_invalid_json_encoding_is_backend_error():
    def handler(request):
        if request.url.host == "llm":
            return httpx.Response(200, content=b'"\xff"')
        return httpx.Response(200, json=jev_response())
    llm, jev = run_pair(handler)
    assert llm.error
    assert jev.decision


@pytest.mark.parametrize("status", [200, 404])
def test_http_exchange_preserves_original_payload_and_json_error(status):
    def handler(request):
        if request.url.host == "jev":
            return httpx.Response(200, json=jev_response())
        return httpx.Response(status, json=llm_response() if status == 200 else {"error": "missing model"})
    llm, _ = run_pair(handler, request="원본" * 1000)
    assert llm.http.request_body["messages"][1]["content"] == "원본" * 1000
    assert llm.http.status_code == status
    assert llm.http.response_is_json
    assert json.loads(llm.http.response_text) == llm.http.response_json
    if status == 404:
        assert llm.http.response_json == {"error": "missing model"}


def test_timeout_keeps_request_without_response():
    def handler(request):
        raise httpx.ReadTimeout("timeout", request=request)
    llm, _ = run_pair(handler)
    assert llm.http.request_body["stream"] is False
    assert llm.http.status_code is None
    assert llm.http.response_text is None
