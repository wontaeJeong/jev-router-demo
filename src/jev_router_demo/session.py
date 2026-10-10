"""Frontend-independent, incremental comparison and session measurements."""

import asyncio
from dataclasses import asdict, fields

import httpx

from jev_router_demo.config import Config
from jev_router_demo.comparison import decision_rows
from jev_router_demo.inspection import inspector_data
from jev_router_demo.metrics import RouterMetrics
from jev_router_demo.routers.litellm import LiteLLMRouter
from jev_router_demo.routers.factory import create_jev_router


def safe_display(value):
    """Make malformed returned Unicode inspectable on UTF-8 frontends."""
    if isinstance(value, str):
        return value.encode("utf-8", errors="backslashreplace").decode("utf-8")
    if isinstance(value, dict):
        return {safe_display(key): safe_display(child) for key, child in value.items()}
    if isinstance(value, list):
        return [safe_display(child) for child in value]
    return value


class DemoSession:
    def __init__(self, config: Config, client: httpx.AsyncClient):
        self.routers = {"LLM": LiteLLMRouter(client, config), "JEV": create_jev_router(client, config)}
        self.jev_api_mode = config.jev_api_mode
        self.models = {"LLM": config.llm_model, "JEV": config.jev_model}
        self.api_modes = {"LLM": "chat-completions", "JEV": config.jev_api_mode}
        self.metrics = {name: RouterMetrics() for name in self.routers}
        self.states = dict.fromkeys(self.routers, "idle")
        self.results = {}
        self.running = False
        self.run_id = 0
        self.request = ""
        self.scenario_id = None

    def snapshot(self) -> dict:
        results = {}
        for name, result in self.results.items():
            # Raw envelopes can be deeply nested malformed data. Do not copy
            # them recursively just to discard them from frontend snapshots.
            data = {field.name: getattr(result, field.name) for field in fields(result)
                    if field.name not in {"http", "raw_response", "decision"}}
            data["decision"] = result.decision.model_dump() if result.decision else None
            data["model"] = self.models[name]
            data["inspector"] = inspector_data(result)
            data["http"] = {"method": result.http.method, "url": result.http.url, "status_code": result.http.status_code} if result.http else None
            results[name] = data
        metrics = {name: asdict(metric) | {"average_latency_ms": metric.average_latency_ms} for name, metric in self.metrics.items()}
        comparison = {"latency_ratio": None, "output_token_difference": None}
        llm, jev = self.results.get("LLM"), self.results.get("JEV")
        if llm and jev and not llm.error and not jev.error and llm.decision and jev.decision:
            if llm.latency_ms > 0 and jev.latency_ms > 0:
                comparison["latency_ratio"] = llm.latency_ms / jev.latency_ms
            if llm.output_tokens is not None and jev.output_tokens is not None:
                comparison["output_token_difference"] = llm.output_tokens - jev.output_tokens
        return safe_display({"run_id": self.run_id, "running": self.running, "scenario_id": self.scenario_id, "api_modes": self.api_modes,
                             "states": dict(self.states), "results": results, "metrics": metrics, "comparison": comparison,
                             "decision_rows": decision_rows(self.results)})

    async def run(self, request: str, scenario_id: int | None = None):
        if self.running:
            raise ValueError("이미 비교가 실행 중입니다.")
        if not request.strip():
            raise ValueError("요청 내용을 입력해 주세요.")
        self.running = True
        self.run_id += 1
        self.request, self.scenario_id = request, scenario_id
        self.results = {}
        self.states = dict.fromkeys(self.routers, "running")
        tasks = []
        try:
            tasks = [asyncio.create_task(router.route(request)) for router in self.routers.values()]
            yield {"type": "started", "run_id": self.run_id, "snapshot": self.snapshot()}
            for completed in asyncio.as_completed(tasks):
                result = await completed
                name = result.router_name
                self.results[name] = result
                self.states[name] = "success" if result.decision and not result.error else "error"
                self.metrics[name].add(result)
                yield {"type": "result", "run_id": self.run_id, "router": name, "snapshot": self.snapshot()}
            self.running = False
            yield {"type": "finished", "run_id": self.run_id, "snapshot": self.snapshot()}
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            self.running = False
            for name, state in self.states.items():
                if state == "running":
                    self.states[name] = "idle"
