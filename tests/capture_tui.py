"""Render wide/narrow TUI smoke artifacts with synthetic HTTP responses.

Run: uv run python tests/capture_tui.py
Artifacts: exports/tui-*.svg (ignored by Git).
"""

import asyncio
from dataclasses import replace
from pathlib import Path

import httpx

from jev_router_demo.tui import RouterDemoApp
from test_routers import CONFIG, llm_response
from test_systemone import typed_response


async def capture():
    def handler(request):
        return httpx.Response(200, json=llm_response() if request.url.host == "llm" else typed_response())
    directory = Path("exports")
    directory.mkdir(exist_ok=True)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        app = RouterDemoApp(replace(CONFIG, jev_api_mode="systemone", jev_model="typesafe/jev-1.13"), client)
        async with app.run_test(size=(120, 42)) as pilot:
            await pilot.press("r")
            await app.workers.wait_for_complete()
            await pilot.pause()
            app.save_screenshot("tui-wide.svg", path=str(directory))
            await pilot.resize_terminal(70, 30)
            await pilot.pause()
            app.save_screenshot("tui-narrow.svg", path=str(directory))
            await pilot.press("o")
            await pilot.pause()
            app.save_screenshot("tui-inspector.svg", path=str(directory))
    print("Synthetic TUI screenshots saved in exports/")


if __name__ == "__main__":
    asyncio.run(capture())
