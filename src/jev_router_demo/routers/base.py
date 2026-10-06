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
        result.error = "Unexpected API response: missing generated decision text."
        return result
    try:
        result.generated_bytes = len(
            (result.generated_text + (result.thinking_text or "")).encode("utf-8")
        )
    except UnicodeEncodeError:
        result.error = "Unexpected API response: invalid Unicode in generated content."
        return result
    started = perf_counter()
    try:
        result.decision = parse_decision(result.generated_text)
        result.parse_success = True
    except ValidationError as exc:
        result.parse_success = False
        first = exc.errors(include_url=False)[0]
        if first["type"] == "json_invalid":
            result.error = "Invalid JSON in generated routing output."
        else:
            field = ".".join(str(part) for part in first["loc"]) or "decision"
            result.error = f"Malformed routing result: {field}: {first['msg']}"
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
            result.error = "Unexpected API response: expected a JSON object."
        else:
            result = parser(data)
    except httpx.TimeoutException:
        result.error = f"Request timed out after {timeout:g} seconds."
    except httpx.ConnectError:
        result.error = "Cannot connect (connection refused or unavailable endpoint). Check URL and service."
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:250]
        result.error = f"HTTP {exc.response.status_code}: {detail} (check model name/configuration)."
    except httpx.RequestError as exc:
        result.error = f"Network error: {exc}"
    except httpx.InvalidURL as exc:
        result.error = f"Invalid endpoint URL: {exc}"
    except json.JSONDecodeError:
        result.error = "Invalid JSON in API response."
    except UnicodeDecodeError:
        result.error = "Invalid Unicode encoding in API JSON response."
    except RecursionError:
        result.error = "API JSON response exceeds supported nesting depth. Inspect HTTP raw text."
    finally:
        result.latency_ms = (perf_counter() - started) * 1000
        result.http = exchange
    return result
