import asyncio

import httpx
from textual.widgets import Select, TextArea

from jev_router_demo.tui import RouterDemoApp
from test_routers import CONFIG, jev_response, llm_response


def test_navigation_editor_and_narrow_layout():
    async def check():
        app = RouterDemoApp(CONFIG)
        async with app.run_test(size=(120, 42)) as pilot:
            await pilot.press("n")
            assert app.scenario.label == "FastAPI Concurrency"
            await pilot.press("e")
            editor = app.screen.query_one("#request-editor", TextArea)
            editor.load_text("Custom request\nDo not execute r n p q")
            await pilot.click("#save-request")
            assert app.scenario.request == "Custom request\nDo not execute r n p q"
            await pilot.resize_terminal(70, 30)
            assert app.query_one("#cards").has_class("narrow")
            await pilot.press("e", "escape")
            assert app.scenario.label == "Custom"
    asyncio.run(check())


def test_partial_result_and_full_inspector(tmp_path):
    async def check():
        release = asyncio.Event()
        async def handler(request):
            if request.url.host == "llm":
                await release.wait()
                return httpx.Response(200, json=llm_response())
            return httpx.Response(200, json=jev_response())
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            app = RouterDemoApp(CONFIG, client)
            async with app.run_test(size=(120, 45)) as pilot:
                await pilot.press("r")
                for _ in range(30):
                    await pilot.pause(0.01)
                    if app.session.states["JEV"] == "success":
                        break
                assert app.session.states == {"LLM": "running", "JEV": "success"}
                assert app.query_one("#scenario", Select).disabled
                release.set()
                await app.workers.wait_for_complete()
                await pilot.press("o")
                app.query_one("#router", Select).value = "LLM"
                await pilot.pause()
                assert "중략" in app.inspector_text
                await pilot.click("#full-toggle")
                assert "중략" not in app.inspector_text
                assert not app.query_one("#scenario", Select).disabled
                await pilot.resize_terminal(70, 30)
                await pilot.pause()
                assert app.query_one("#json-log").region.height >= 5
    asyncio.run(check())


def test_custom_selection_opens_editor_and_cancel_restores_scenario():
    async def check():
        app = RouterDemoApp(CONFIG)
        async with app.run_test(size=(100, 40)) as pilot:
            app.query_one("#scenario", Select).value = -1
            await pilot.pause()
            assert app.screen.query("#request-editor")
            await pilot.press("escape")
            assert app.query_one("#scenario", Select).value == 0
            assert app.scenario.label == "Python Utility"
    asyncio.run(check())


def test_multiline_preview_is_keyboard_scrollable():
    async def check():
        app = RouterDemoApp(CONFIG)
        async with app.run_test(size=(70, 30)) as pilot:
            await pilot.press("e")
            app.screen.query_one("#request-editor", TextArea).load_text("line\n" * 100)
            await pilot.click("#save-request")
            preview = app.query_one("#request-preview-scroll")
            preview.focus()
            await pilot.press("end")
            await pilot.pause()
            assert preview.scroll_y > 0
    asyncio.run(check())
