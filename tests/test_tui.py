import asyncio

import httpx
from rich.console import Console
from textual.widgets import Select, Static, TextArea
from textual.containers import VerticalScroll
from textual.geometry import Region

from jev_router_demo.tui import RouterDemoApp
from jev_router_demo.models import RoutingDecision, RoutingResult
from jev_router_demo.scenarios import SCENARIOS
from test_routers import CONFIG, jev_response, llm_response


def test_summary_is_displayed_but_cleared_when_request_is_edited():
    async def check():
        app = RouterDemoApp(CONFIG)
        async with app.run_test(size=(120, 42)) as pilot:
            preview = app.query_one("#request-preview", Static)
            assert "요청 요약" in str(preview.content)
            assert SCENARIOS[0].summary in str(preview.content)
            assert SCENARIOS[0].request not in str(preview.content)
            await pilot.press("x")
            assert SCENARIOS[0].request in str(app.query_one("#request-original", Static).content)
            await pilot.press("e")
            app.screen.query_one("#request-editor", TextArea).load_text("A different request")
            await pilot.click("#save-request")
            assert "요청 요약" not in str(preview.content)
            assert "A different request" in str(preview.content)
            assert app.scenario.summary is None
    asyncio.run(check())


def test_navigation_editor_and_narrow_layout():
    async def check():
        app = RouterDemoApp(CONFIG)
        async with app.run_test(size=(120, 42)) as pilot:
            await pilot.press("n")
            assert app.scenario.label == "FastAPI 동시성 오류"
            await pilot.press("e")
            editor = app.screen.query_one("#request-editor", TextArea)
            editor.load_text("Custom request\nDo not execute r n p q")
            await pilot.click("#save-request")
            assert app.scenario.request == "Custom request\nDo not execute r n p q"
            await pilot.resize_terminal(70, 30)
            assert app.query_one("#choices-LLM-model_tier").region.y == app.query_one("#choices-JEV-model_tier").region.y
            await pilot.resize_terminal(50, 30)
            assert app.query_one("#pair-model_tier").has_class("narrow")
            await pilot.press("e", "escape")
            assert app.scenario.label == "직접 입력"
    asyncio.run(check())


def test_primary_comparison_shows_all_candidates_probabilities_and_aligned_choices():
    async def check():
        app = RouterDemoApp(CONFIG)
        async with app.run_test(size=(120, 42)) as pilot:
            app.session.results["JEV"] = RoutingResult("JEV", decision=RoutingDecision(
                model_tier="standard", needs_web=False, needs_approval=True),
                probabilities={"model_tier": {"fast": 0.8, "standard": 0.2},
                               "needs_web": {"false": 0.0}})
            app.session.states = {"LLM": "running", "JEV": "success"}
            app.refresh_results()
            await pilot.pause()
            console = Console(width=50, color_system=None)
            with console.capture() as capture:
                console.print(app.query_one("#choices-JEV-model_tier", Static).content)
            lines = capture.get().splitlines()
            assert any("●" in line and "일반 처리" in line and "20.0%" in line and "선택" in line for line in lines)
            assert any("○" in line and "빠른 처리" in line and "80.0%" in line for line in lines)
            assert any("심층 추론" in line and "미제공" in line for line in lines)
            for width in (120, 70, 64):
                await pilot.resize_terminal(width, 42)
                for field in ("model_tier", "needs_web", "needs_approval"):
                    left = app.query_one(f"#choices-LLM-{field}")
                    right = app.query_one(f"#choices-JEV-{field}")
                    assert left.region.y == right.region.y
                    assert left.region.right <= right.region.x
                    assert left.region.height == right.region.height
                zero_choice = app.query_one("#choices-JEV-needs_web", Static)
                rendered = "\n".join(strip.text for strip in zero_choice.render_lines(
                    Region(0, 0, zero_choice.size.width, zero_choice.size.height)))
                assert any("●" in line and "불필요" in line and "0.0%" in line and "선택" in line
                           for line in rendered.splitlines())
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
            assert app.scenario.label == "Python 간단한 활용"
    asyncio.run(check())


def test_multiline_preview_is_keyboard_scrollable():
    async def check():
        app = RouterDemoApp(CONFIG)
        async with app.run_test(size=(70, 30)) as pilot:
            await pilot.press("e")
            request = "\n\n" + "line\n" * 100 + "middle sentinel\n" + "tail\n" * 100
            app.screen.query_one("#request-editor", TextArea).load_text(request)
            await pilot.click("#save-request")
            assert "line" in str(app.query_one("#request-preview", Static).content)
            await pilot.press("x")
            assert request in str(app.query_one("#request-original", Static).content)
            preview = app.query_one("#request-original-scroll")
            preview.focus()
            await pilot.press("end")
            await pilot.pause()
            assert preview.scroll_y > 0
    asyncio.run(check())


def test_selected_candidate_is_actual_answer_not_probability_argmax():
    from jev_router_demo.tui import probability_content

    result = RoutingResult("JEV", decision=RoutingDecision(
        model_tier="standard", needs_web=False, needs_approval=True),
        probabilities={"model_tier": {"fast": 0.8, "standard": 0.2},
                       "needs_web": {"true": 0.0, "false": 1.0}})
    console = Console(width=60, color_system=None)
    with console.capture() as capture:
        console.print(probability_content("JEV", "model", "success", result))
    lines = capture.get().splitlines()
    assert any("▶" in line and "일반 처리" in line and "20.0%" in line for line in lines)
    assert any("빠른 처리" in line and "80.0%" in line and "▶" not in line for line in lines)
    assert any("▶" in line and "불필요" in line and "100.0%" in line for line in lines)
    assert any("필요" in line and "0.0%" in line for line in lines)
    assert "사용자 승인" in capture.get() and "미제공" in capture.get()
    assert "█" in capture.get()


def test_summary_and_details_remain_accessible_on_short_terminal():
    async def check():
        app = RouterDemoApp(CONFIG)
        async with app.run_test(size=(80, 24)) as pilot:
            app.session.results["LLM"] = RoutingResult("LLM", decision=RoutingDecision(
                model_tier="fast", needs_web=False, needs_approval=False))
            app.session.results["JEV"] = RoutingResult("JEV", decision=RoutingDecision(
                model_tier="standard", needs_web=True, needs_approval=False), output_kind="typed")
            app.refresh_results()
            summary = str(app.query_one("#comparison-summary", Static).content)
            assert "모델 등급" in summary and "웹 검색" in summary
            await pilot.press("d")
            target = app.query_one("#probability-JEV", Static)
            scroll = app.query_one("#decisions VerticalScroll", VerticalScroll)
            scroll.focus()
            await pilot.press("end")
            await pilot.pause()
            assert target.region.intersection(scroll.content_region).height > 0
            console = Console(width=60, color_system=None)
            with console.capture() as capture:
                console.print(app.query_one("#probability-JEV", Static).content)
            assert "미제공" in capture.get()
            await pilot.press("x")
            assert app.query_one("#request-original-scroll").region.height >= 5
            await pilot.press("c")
            scroll = app.query_one("#comparison VerticalScroll", VerticalScroll)
            scroll.focus()
            await pilot.press("end")
            await pilot.pause()
            assert app.query_one("#comparison-summary").region.intersection(scroll.content_region).height > 0
    asyncio.run(check())


def test_finished_failure_does_not_show_waiting_for_decisions():
    async def check():
        def handler(request):
            return httpx.Response(500, text="backend failed")
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            app = RouterDemoApp(CONFIG, client)
            async with app.run_test(size=(120, 42)) as pilot:
                await pilot.press("r")
                await app.workers.wait_for_complete()
                summary = str(app.query_one("#comparison-summary", Static).content)
                assert "기다리는 중" not in summary
                assert "비교 불가" in summary
    asyncio.run(check())
