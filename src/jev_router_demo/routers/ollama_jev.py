"""Standard Ollama generation fallback, not an assumed typed Jev decision API.

When the real Jev contract is confirmed, change build_jev_prompt and
parse_jev_response here. Candidate confidence must come from that contract,
not generated explanations or Ollama's token-level logprobs.
"""

from typing import Any

import httpx

from jev_router_demo.config import Config
from jev_router_demo.models import ROUTING_POLICY, RoutingResult
from jev_router_demo.routers.base import parse_generated, request_route, token_count


def build_jev_prompt(request: str) -> str:
    return (
        f"STATE\n\n{request}\n\nDECISIONS\n\n"
        "model_tier:\n- FAST\n- STANDARD\n- REASONING\n\n"
        "needs_web:\n- YES\n- NO\n\nneeds_approval:\n- YES\n- NO\n\n"
        "Return these decisions as JSON: model_tier in lowercase, "
        "needs_web and needs_approval as JSON booleans."
    )


def parse_jev_response(response: dict[str, Any]) -> RoutingResult:
    """Only the standard /api/generate envelope is currently supported."""
    result = RoutingResult("JEV", raw_response=response)
    result.input_tokens = token_count(response.get("prompt_eval_count"))
    result.output_tokens = token_count(response.get("eval_count"))
    if result.input_tokens is not None and result.output_tokens is not None:
        result.total_tokens = result.input_tokens + result.output_tokens
    if "error" in response:
        result.error = f"Ollama error: {str(response['error'])[:250]}"
        return result
    if response.get("done") is not True:
        result.error = "Unexpected API response: Ollama generation is not complete."
        return result
    if not isinstance(response.get("response"), str):
        result.error = "Unexpected API response: missing Ollama response text."
        return result
    result.generated_text = response["response"]
    thinking = response.get("thinking")
    if isinstance(thinking, str):
        result.thinking_text = thinking
    return parse_generated(result)


class OllamaJevRouter:
    def __init__(self, client: httpx.AsyncClient, config: Config) -> None:
        self.client = client
        self.config = config

    async def route(self, request: str) -> RoutingResult:
        payload = {
            "model": self.config.jev_model,
            "system": ROUTING_POLICY,
            "prompt": build_jev_prompt(request),
            "stream": False,
            "format": "json",
        }
        return await request_route(
            self.client, self.config.jev_url,
            payload, "JEV", parse_jev_response, self.config.request_timeout,
        )
