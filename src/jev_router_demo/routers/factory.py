import httpx

from jev_router_demo.config import Config
from jev_router_demo.routers.systemone import SystemOneRouter


def create_jev_router(client: httpx.AsyncClient, config: Config) -> SystemOneRouter:
    if config.jev_api_mode in {"systemone", "decisions"}:
        return SystemOneRouter(client, config)
    raise ValueError("Unknown Jev API mode")
