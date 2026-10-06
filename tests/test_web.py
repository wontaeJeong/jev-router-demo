import asyncio

import httpx
from fastapi.testclient import TestClient

from jev_router_demo.web import create_app
from test_routers import CONFIG, jev_response, llm_response


def test_web_assets_run_and_isolated_sessions():
    async def handler(request):
        if request.url.host == "llm":
            await asyncio.sleep(0.05)
            return httpx.Response(200, json=llm_response())
        return httpx.Response(200, json=jev_response())
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with TestClient(create_app(CONFIG, client)) as browser:
        assert browser.get("/").status_code == 200
        assert browser.get("/static/app.js").status_code == 200
        with browser.websocket_connect("/ws") as socket:
            assert socket.receive_json()["type"] == "init"
            socket.send_json({"type": "run", "request": "x" * 2000, "scenario_id": None})
            assert socket.receive_json()["type"] == "started"
            first = socket.receive_json()
            assert first["router"] == "JEV"
            second = socket.receive_json()
            assert second["router"] == "LLM"
            finished = socket.receive_json()
            assert finished["type"] == "finished"
            assert finished["snapshot"]["metrics"]["LLM"]["requests"] == 1
            assert "중략" in second["snapshot"]["results"]["LLM"]["inspector"]["request"]["preview"]
        with browser.websocket_connect("/ws") as socket:
            assert socket.receive_json()["snapshot"]["metrics"]["LLM"]["requests"] == 0


def test_invalid_commands_and_duplicate_run_do_not_kill_session():
    async def handler(request):
        await asyncio.sleep(0.1)
        return httpx.Response(404, json={"error": "Model missing"})
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with TestClient(create_app(CONFIG, client)) as browser, browser.websocket_connect("/ws") as socket:
        socket.receive_json()
        for command in ["broken", '{"type":"run","request":" "}', '{"type":"run","request":42}', '{"type":"run","request":"ok","scenario_id":99}']:
            socket.send_text(command)
            assert socket.receive_json()["type"] == "error"
        socket.send_json({"type": "run", "request": "ok"})
        assert socket.receive_json()["type"] == "started"
        socket.send_json({"type": "run", "request": "duplicate"})
        assert socket.receive_json()["type"] == "error"
        result = socket.receive_json()
        assert result["snapshot"]["results"][result["router"]]["inspector"]["response"]["full"].find("Model missing") >= 0
        socket.receive_json()
        finished = socket.receive_json()
        assert finished["type"] == "finished"
        assert finished["snapshot"]["states"] == {"LLM": "error", "JEV": "error"}
