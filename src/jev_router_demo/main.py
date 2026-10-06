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
from jev_router_demo.scenarios import SCENARIOS, Scenario
from jev_router_demo.ui import render_screen, show_raw_outputs


async def compare(
    request: str, llm: LiteLLMRouter, jev: OllamaJevRouter,
) -> tuple[RoutingResult, RoutingResult]:
    llm_result, jev_result = await asyncio.gather(llm.route(request), jev.route(request))
    return llm_result, jev_result


async def interactive(config: Config, console: Console) -> None:
    index = 0
    scenario = SCENARIOS[index]
    results = None
    metrics = {"LLM": RouterMetrics(), "JEV": RouterMetrics()}
    message = "Commands use Enter. Both routers use actual endpoint responses."
    async with httpx.AsyncClient() as client:
        llm = LiteLLMRouter(client, config)
        jev = OllamaJevRouter(client, config)
        while True:
            render_screen(console, scenario, index, results, metrics, message)
            command = console.input("\nCommand > ").strip().lower()
            message = ""
            if command == "q":
                return
            if command == "r":
                console.print(Text("Routing request… LLM + Jev-like (concurrent)", style="cyan"))
                with console.status("Waiting for router responses…", spinner="dots"):
                    results = await compare(scenario.request, llm, jev)
                for result in results:
                    metrics[result.router_name].add(result)
            elif command in {"n", "p"}:
                index = (index + (1 if command == "n" else -1)) % len(SCENARIOS)
                scenario = SCENARIOS[index]
                results = None
            elif command == "e":
                request = console.input("Request > ")
                if request.strip():
                    scenario = Scenario("Custom", request)
                    results = None
                    message = "Custom request ready. Press r then Enter to run."
                else:
                    message = "Empty request ignored."
            elif command == "v":
                console.print(Panel(Text(scenario.request), title="Full request"))
                console.input("Enter to return > ")
            elif command == "o":
                if results:
                    show_raw_outputs(console, results)
                else:
                    console.print("Run a request first to inspect its outputs.")
                console.input("Enter to return > ")
            else:
                message = "Choose r, n, p, e, v, o or q."


def main() -> None:
    parser = argparse.ArgumentParser(description="Live router comparison: terminal TUI or local web dashboard")
    parser.add_argument("--web", action="store_true", help="serve the local web dashboard")
    parser.add_argument("--port", type=int, default=8000, help="local web port (default: 8000)")
    parser.add_argument("--cli", action="store_true", help="use the original line-oriented CLI")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
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
            console.print(f"Router dashboard: http://127.0.0.1:{args.port}")
            uvicorn.run(create_app(config), host="127.0.0.1", port=args.port)
        elif args.cli or not sys.stdin.isatty():
            asyncio.run(interactive(config, console))
        else:
            from jev_router_demo.tui import RouterDemoApp
            RouterDemoApp(config).run()
    except (EOFError, KeyboardInterrupt):
        console.print("\nGoodbye.")
