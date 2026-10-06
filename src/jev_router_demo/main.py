import asyncio
import argparse
import sys

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from jev_router_demo.config import Config, load_config
from jev_router_demo.metrics import RouterMetrics
from jev_router_demo.models import RoutingResult
from jev_router_demo.routers.litellm import LiteLLMRouter
from jev_router_demo.routers.ollama_jev import OllamaJevRouter
from jev_router_demo.routers.systemone import SystemOneRouter
from jev_router_demo.routers.factory import create_jev_router
from jev_router_demo.scenarios import SCENARIOS, Scenario
from jev_router_demo.ui import render_screen, show_raw_outputs


async def compare(
    request: str, llm: LiteLLMRouter, jev: OllamaJevRouter | SystemOneRouter,
) -> tuple[RoutingResult, RoutingResult]:
    llm_result, jev_result = await asyncio.gather(llm.route(request), jev.route(request))
    return llm_result, jev_result


async def interactive(config: Config, console: Console) -> None:
    index = 0
    scenario = SCENARIOS[index]
    results = None
    metrics = {"LLM": RouterMetrics(), "JEV": RouterMetrics()}
    message = "명령 입력 후 Enter를 누르세요. 두 라우터의 실제 API 응답을 사용합니다."
    async with httpx.AsyncClient() as client:
        llm = LiteLLMRouter(client, config)
        jev = create_jev_router(client, config)
        while True:
            render_screen(console, scenario, index, results, metrics, message)
            command = console.input("\n명령 > ").strip().lower()
            message = ""
            if command == "q":
                return
            if command == "r":
                console.print(Text("요청 라우팅 중… LLM + Jev (동시 실행)", style="cyan"))
                with console.status("라우터 응답을 기다리는 중…", spinner="dots"):
                    results = await compare(scenario.request, llm, jev)
                for result in results:
                    metrics[result.router_name].add(result)
            elif command in {"n", "p"}:
                index = (index + (1 if command == "n" else -1)) % len(SCENARIOS)
                scenario = SCENARIOS[index]
                results = None
            elif command == "e":
                request = console.input("요청 > ")
                if request.strip():
                    scenario = Scenario("직접 입력", request)
                    results = None
                    message = "직접 입력 요청이 준비되었습니다. r 입력 후 Enter를 눌러 실행하세요."
                else:
                    message = "빈 요청은 적용하지 않았습니다."
            elif command == "v":
                console.print(Panel(Text(scenario.request), title="요청 원문 전체"))
                console.input("Enter를 눌러 돌아가기 > ")
            elif command == "o":
                if results:
                    show_raw_outputs(console, results)
                else:
                    console.print("출력을 확인하려면 먼저 요청을 실행해 주세요.")
                console.input("Enter를 눌러 돌아가기 > ")
            else:
                message = "r, n, p, e, v, o, q 중에서 선택해 주세요."


def main() -> None:
    parser = argparse.ArgumentParser(description="실시간 라우터 비교: 터미널 UI 또는 로컬 웹 대시보드")
    parser.add_argument("--web", action="store_true", help="로컬 웹 대시보드 실행")
    parser.add_argument("--port", type=int, default=8000, help="로컬 웹 포트 (기본값: 8000)")
    parser.add_argument("--cli", action="store_true", help="줄 단위 명령을 입력하는 기존 CLI 사용")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port는 1부터 65535 사이여야 합니다")
    console = Console()
    try:
        config = load_config()
    except ValueError as exc:
        console.print(Text(str(exc), style="bold red"))
        raise SystemExit(1) from None
    try:
        if args.web:
            import uvicorn
            from jev_router_demo.web import create_app
            console.print(f"라우터 대시보드: http://127.0.0.1:{args.port}")
            uvicorn.run(create_app(config), host="127.0.0.1", port=args.port)
        elif args.cli or not sys.stdin.isatty():
            asyncio.run(interactive(config, console))
        else:
            from jev_router_demo.tui import RouterDemoApp
            RouterDemoApp(config).run()
    except (EOFError, KeyboardInterrupt):
        console.print("\n종료합니다.")
