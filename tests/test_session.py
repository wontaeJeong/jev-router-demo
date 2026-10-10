import asyncio
import json

import httpx
import pytest

from jev_router_demo.session import DemoSession
from jev_router_demo.models import RoutingDecision, RoutingResult
from test_routers import CONFIG, jev_response, llm_response


def test_early_result_and_exactly_once_metrics():
    async def check():
        release = asyncio.Event()
        async def handler(request):
            if request.url.host == "llm":
                await release.wait()
                return httpx.Response(200, json=llm_response())
            return httpx.Response(200, json=jev_response())
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            session = DemoSession(CONFIG, client)
            stream = session.run("x" * 2000, 0)
            started = await anext(stream)
            assert started["type"] == "started"
            assert started["snapshot"]["states"] == {"LLM": "running", "JEV": "running"}
            first = await asyncio.wait_for(anext(stream), 1)
            assert first["router"] == "JEV"
            assert first["snapshot"]["states"]["LLM"] == "running"
            with pytest.raises(ValueError, match="실행 중"):
                await anext(session.run("duplicate"))
            release.set()
            rest = [event async for event in stream]
            assert rest[-1]["type"] == "finished"
            assert session.metrics["JEV"].requests == session.metrics["LLM"].requests == 1
            request_data = rest[-1]["snapshot"]["results"]["LLM"]["inspector"]["request"]
            assert "중략" in request_data["preview"]
            assert json.loads(request_data["full"])["messages"][1]["content"] == "x" * 2000
    asyncio.run(check())


def test_comparison_rows_preserve_candidate_order_actual_selection_and_missing_probabilities():
    async def check():
        async with httpx.AsyncClient() as client:
            session = DemoSession(CONFIG, client)
            session.results = {
                "LLM": RoutingResult("LLM", decision=RoutingDecision(
                    model_tier="fast", needs_web=False, needs_approval=False)),
                "JEV": RoutingResult("JEV", decision=RoutingDecision(
                    model_tier="standard", needs_web=True, needs_approval=False),
                    probabilities={"model_tier": {"standard": 0.2, "fast": 0.8},
                                   "needs_web": {"false": 0.0, "true": 1.0}}),
            }
            rows = session.snapshot()["decision_rows"]
            assert [row["field"] for row in rows] == ["model_tier", "needs_web", "needs_approval"]
            assert [row["different"] for row in rows] == [True, True, False]
            for name in ("LLM", "JEV"):
                assert [entry["value"] for entry in rows[0]["routers"][name]] == ["fast", "standard", "reasoning"]
            assert rows[0]["routers"]["LLM"][0]["selected"] is True
            assert rows[0]["routers"]["LLM"][0]["probability"] is None
            assert rows[0]["routers"]["JEV"][0]["selected"] is False
            assert rows[0]["routers"]["JEV"][1]["selected"] is True
            assert rows[0]["routers"]["JEV"][1]["probability"] == 0.2
            assert rows[0]["routers"]["JEV"][2]["probability"] is None
            assert rows[1]["routers"]["JEV"][1]["probability"] == 0.0
            session.results.clear()
            cleared = session.snapshot()["decision_rows"]
            assert not any(entry["selected"] for row in cleared for entries in row["routers"].values() for entry in entries)
            assert not any(row["different"] for row in cleared)
    asyncio.run(check())


def test_error_isolated_and_comparison_unavailable():
    async def check():
        def handler(request):
            return httpx.Response(503, json={"error": "offline"}) if request.url.host == "llm" else httpx.Response(200, json=jev_response())
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            session = DemoSession(CONFIG, client)
            events = [event async for event in session.run("request")]
            snapshot = events[-1]["snapshot"]
            assert snapshot["states"] == {"LLM": "error", "JEV": "success"}
            assert snapshot["comparison"]["latency_ratio"] is None
            assert snapshot["metrics"]["LLM"]["errors"] == 1
            assert snapshot["metrics"]["LLM"]["average_latency_ms"] is None
    asyncio.run(check())


def test_closing_run_cancels_unfinished_calls():
    async def check():
        cancelled = []
        async def handler(request):
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.append(request.url.host)
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            session = DemoSession(CONFIG, client)
            stream = session.run("request")
            await anext(stream)
            waiting = asyncio.create_task(anext(stream))
            await asyncio.sleep(0.02)
            waiting.cancel()
            with pytest.raises(asyncio.CancelledError):
                await waiting
            await stream.aclose()
            assert sorted(cancelled) == ["jev", "llm"]
            assert not session.running
            assert session.metrics["LLM"].requests == 0
    asyncio.run(check())


def test_empty_request_is_rejected_before_network():
    async def check():
        async with httpx.AsyncClient() as client:
            with pytest.raises(ValueError, match="요청 내용을 입력"):
                await anext(DemoSession(CONFIG, client).run(" \n"))
    asyncio.run(check())


@pytest.mark.parametrize("depth", [1100, 10000])
def test_deep_malformed_response_does_not_cancel_healthy_backend(depth):
    raw = "[" * depth + "0" + "]" * depth
    async def check():
        async def handler(request):
            if request.url.host == "llm":
                return httpx.Response(200, text=raw)
            await asyncio.sleep(0.02)
            return httpx.Response(200, json=jev_response())
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            session = DemoSession(CONFIG, client)
            events = [event async for event in session.run("request")]
            assert events[-1]["type"] == "finished"
            assert session.states == {"LLM": "error", "JEV": "success"}
            assert session.metrics["JEV"].successes == 1
            assert events[-1]["snapshot"]["results"]["LLM"]["inspector"]["raw"]["full"] == raw
    asyncio.run(check())
