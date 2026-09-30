import asyncio
import json

import httpx
import pytest

from jev_router_demo.config import Config
from jev_router_demo.main import compare
from jev_router_demo.routers.litellm import LiteLLMRouter
from jev_router_demo.routers.ollama_jev import OllamaJevRouter, parse_jev_response


DECISION = {"model_tier": "reasoning", "needs_web": True, "needs_approval": False}
TEXT = json.dumps(DECISION)
CONFIG = Config("http://llm/v1", "baseline", "http://jev", "jev-like")


def llm_response(text=TEXT):
    return {"choices": [{"message": {"content": text}}], "usage": {
        "prompt_tokens": 12, "completion_tokens": 5, "total_tokens": 17,
    }}


def jev_response(text=TEXT):
    return {"response": text, "done": True, "prompt_eval_count": 9, "eval_count": 4}


def run_pair(handler, config=CONFIG, request="Full original request\nwith another line."):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await compare(request, LiteLLMRouter(client, config), OllamaJevRouter(client, config))
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
            assert request.url.path == "/api/generate"
            assert original in body["prompt"]
            assert body["stream"] is False
            assert "authorization" not in request.headers
            return httpx.Response(200, json=jev_response())

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            llm, jev = await compare(original, LiteLLMRouter(client, CONFIG), OllamaJevRouter(client, CONFIG))
        assert llm.decision == jev.decision
        assert (llm.input_tokens, llm.output_tokens, llm.total_tokens) == (12, 5, 17)
        assert (jev.input_tokens, jev.output_tokens, jev.total_tokens) == (9, 4, 13)
        for result in [llm, jev]:
            assert result.latency_ms >= result.parse_ms >= 0
            assert result.parse_required and result.parse_success
            assert result.generated_bytes == len(TEXT.encode())
            assert result.probabilities is None
            assert result.output_kind == "generated"
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


@pytest.mark.parametrize("payload", [[], {}, {"response": 5}, {"error": "model not found"}, {"response": TEXT, "done": False}])
def test_ollama_unexpected_response_is_visible(payload):
    def handler(request):
        return httpx.Response(200, json=payload if request.url.host == "jev" else llm_response())
    llm, jev = run_pair(handler)
    assert llm.decision
    assert jev.error


def test_jev_invalid_decision_retains_generation_metrics():
    result = parse_jev_response(jev_response('{"model_tier":"super-smart"}'))
    assert result.parse_success is False
    assert result.error
    assert result.output_tokens == 4
    assert result.generated_text == '{"model_tier":"super-smart"}'


def test_missing_usage_is_not_zero_and_thinking_bytes_are_counted():
    result = parse_jev_response({"response": TEXT, "thinking": "분석", "done": True})
    assert result.input_tokens is None
    assert result.output_tokens is None
    assert result.total_tokens is None
    assert result.generated_bytes == len((TEXT + "분석").encode("utf-8"))
    assert result.thinking_text == "분석"


def test_zero_usage_is_preserved():
    result = parse_jev_response(jev_response() | {"eval_count": 0})
    assert result.output_tokens == 0


@pytest.mark.parametrize("host", ["llm", "jev"])
def test_invalid_generated_unicode_does_not_discard_other_backend(host):
    def handler(request):
        payload = llm_response() if request.url.host == "llm" else jev_response()
        if request.url.host == host:
            if host == "llm":
                payload["choices"][0]["message"]["content"] = "\ud800"
            else:
                payload["thinking"] = "\ud800"
        return httpx.Response(200, content=json.dumps(payload).encode("ascii"))
    llm, jev = run_pair(handler)
    failed, other = (llm, jev) if host == "llm" else (jev, llm)
    assert "Unicode" in failed.error
    assert failed.generated_bytes is None
    assert other.decision


def test_invalid_json_encoding_is_backend_error():
    def handler(request):
        if request.url.host == "llm":
            return httpx.Response(200, content=b'"\xff"')
        return httpx.Response(200, json=jev_response())
    llm, jev = run_pair(handler)
    assert llm.error
    assert jev.decision
