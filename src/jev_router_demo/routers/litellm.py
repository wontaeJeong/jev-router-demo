from typing import Any

import httpx

from jev_router_demo.config import Config
from jev_router_demo.models import ROUTING_POLICY, RoutingResult
from jev_router_demo.routers.base import parse_generated, request_route, token_count


def parse_llm_response(response: dict[str, Any]) -> RoutingResult:
    result = RoutingResult("LLM", raw_response=response)
    usage = response.get("usage")
    if isinstance(usage, dict):
        result.input_tokens = token_count(usage.get("prompt_tokens"))
        result.output_tokens = token_count(usage.get("completion_tokens"))
        result.total_tokens = token_count(usage.get("total_tokens"))
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        result.error = "예상과 다른 API 응답: 채팅 완성 후보가 없습니다."
        return result
    message = choices[0].get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        result.error = "예상과 다른 API 응답: 메시지 내용이 없습니다 (모델과 응답 거부 여부를 확인해 주세요)."
        return result
    result.generated_text = message["content"]
    thinking = message.get("reasoning_content")
    if isinstance(thinking, str):
        result.thinking_text = thinking
    return parse_generated(result)


class LiteLLMRouter:
    def __init__(self, client: httpx.AsyncClient, config: Config) -> None:
        self.client = client
        self.config = config

    async def route(self, request: str) -> RoutingResult:
        headers = {}
        if self.config.llm_api_key:
            headers["Authorization"] = f"Bearer {self.config.llm_api_key}"
        # JSON is still generated and parsed. No schema capability assumption or
        # automatic retry: unsupported output formats should not bias timing.
        payload = {
            "model": self.config.llm_model,
            "messages": [
                {"role": "system", "content": ROUTING_POLICY},
                {"role": "user", "content": request},
            ],
            "stream": False,
        }
        return await request_route(
            self.client, self.config.llm_base_url + "/chat/completions",
            payload, "LLM", parse_llm_response, self.config.request_timeout, headers,
        )
