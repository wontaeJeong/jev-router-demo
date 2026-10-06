"""Deterministic browser smoke fixture. Never used by the real entrypoint.

Run: uv run python tests/browser_demo_server.py
All backend responses here are synthetic fixtures, not performance evidence.
"""

import asyncio
import json

import httpx
import uvicorn

from jev_router_demo.web import create_app
from test_routers import CONFIG, jev_response, llm_response


async def handler(request):
    body = json.loads(request.content)
    user_request = body["messages"][1]["content"] if request.url.host == "llm" else body["prompt"]
    await asyncio.sleep(1.2 if request.url.host == "llm" else 0.15)
    if "__http_error__" in user_request and request.url.host == "llm":
        return httpx.Response(404, json={"error": {"message": "Model missing", "detail": "오류 원본 " * 500}})
    payload = llm_response() if request.url.host == "llm" else jev_response()
    payload["fixture_note"] = "SYNTHETIC BROWSER TEST · " * 100
    if request.url.host == "llm":
        payload["choices"][0]["message"]["reasoning_content"] = "Returned thinking fixture. " * 200
    return httpx.Response(200, json=payload)


if __name__ == "__main__":
    uvicorn.run(create_app(CONFIG, httpx.AsyncClient(transport=httpx.MockTransport(handler))), host="127.0.0.1", port=8765)
