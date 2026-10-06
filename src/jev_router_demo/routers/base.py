import json
from copy import deepcopy
from collections.abc import Callable
from time import perf_counter
from typing import Any

import httpx
from pydantic import ValidationError

from jev_router_demo.models import HttpExchange, RoutingResult, parse_decision


def token_count(value: object) -> int | None:
    """Missing or malformed usage is unavailable, not zero."""
    return value if type(value) is int and value >= 0 else None


def parse_generated(result: RoutingResult) -> RoutingResult:
    """Parse decision text while keeping usage/raw output on validation failure."""
    if result.generated_text is None:
        result.error = "예상과 다른 API 응답: 생성된 결정 텍스트가 없습니다."
        return result
    try:
        result.generated_bytes = len(
            (result.generated_text + (result.thinking_text or "")).encode("utf-8")
        )
    except UnicodeEncodeError:
        result.error = "예상과 다른 API 응답: 생성 내용에 잘못된 Unicode가 포함되어 있습니다."
        return result
    started = perf_counter()
    try:
        result.decision = parse_decision(result.generated_text)
        result.parse_success = True
    except ValidationError as exc:
        result.parse_success = False
        first = exc.errors(include_url=False)[0]
        if first["type"] == "json_invalid":
            result.error = "생성된 라우팅 출력의 JSON 형식이 잘못되었습니다."
        else:
            field = ".".join(str(part) for part in first["loc"]) or "decision"
            result.error = f"라우팅 결과 형식 오류: {field}: {first['msg']}"
    finally:
        result.parse_ms = (perf_counter() - started) * 1000
    return result


async def request_route(
    client: httpx.AsyncClient,
    url: str,
    payload: dict[str, Any],
    router_name: str,
    parser: Callable[[dict[str, Any]], RoutingResult],
    timeout: float,
    headers: dict[str, str] | None = None,
    *,
    output_kind: str = "generated",
) -> RoutingResult:
    """Common transport boundary; decision contracts belong to each adapter."""
    result = RoutingResult(router_name, output_kind=output_kind, parse_required=output_kind == "generated")
    exchange = HttpExchange("POST", url, deepcopy(payload))
    started = perf_counter()
    try:
        response = await client.post(url, json=payload, headers=headers, timeout=timeout)
        exchange.status_code = response.status_code
        exchange.response_text = response.text
        decode_error = None
        try:
            exchange.response_json = response.json()
            exchange.response_is_json = True
        except (json.JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
            decode_error = exc
        # Retain even non-JSON errors for raw inspection.
        result.raw_response = response.text
        response.raise_for_status()
        if decode_error:
            raise decode_error
        data = exchange.response_json
        result.raw_response = data
        if not isinstance(data, dict):
            result.error = "예상과 다른 API 응답: JSON 객체가 필요합니다."
        else:
            result = parser(data)
    except httpx.TimeoutException:
        result.error = f"{timeout:g}초 후 요청 시간이 초과되었습니다."
    except httpx.ConnectError:
        result.error = "연결할 수 없습니다 (연결 거부 또는 엔드포인트 사용 불가). URL과 서비스를 확인해 주세요."
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:250]
        result.error = f"HTTP {exc.response.status_code}: {detail} (모델 이름과 설정을 확인해 주세요)."
    except httpx.RequestError as exc:
        result.error = f"네트워크 오류: {exc}"
    except httpx.InvalidURL as exc:
        result.error = f"잘못된 엔드포인트 URL: {exc}"
    except json.JSONDecodeError:
        result.error = "API 응답의 JSON 형식이 잘못되었습니다."
    except UnicodeDecodeError:
        result.error = "API JSON 응답의 Unicode 인코딩이 잘못되었습니다."
    except RecursionError:
        result.error = "API JSON 응답이 지원하는 중첩 깊이를 초과했습니다. HTTP 원문을 확인해 주세요."
    finally:
        result.latency_ms = (perf_counter() - started) * 1000
        result.http = exchange
    return result
