"""Presentation-only previews; stored and exported content is never shortened."""

import json
from pathlib import Path
from uuid import uuid4

from jev_router_demo.models import RoutingResult


SECTIONS = {"request": "요청 JSON", "response": "응답 JSON", "generated": "생성 출력", "thinking": "추론 내용", "raw": "HTTP 원문"}


def abbreviate(value: object) -> tuple[object, int]:
    if isinstance(value, str):
        if len(value) > 480:
            return value[:320] + f"… [중략: {len(value) - 440}자] …" + value[-120:], 1
        return value, 0
    if isinstance(value, dict):
        output, count = {}, 0
        for key, child in value.items():
            output[key], found = abbreviate(child)
            count += found
        return output, count
    if isinstance(value, list):
        output, count = [], 0
        for child in value:
            preview, found = abbreviate(child)
            output.append(preview)
            count += found
        return output, count
    return value, 0


def section_value(result: RoutingResult, section: str) -> tuple[object, bool]:
    if section not in SECTIONS:
        raise ValueError("알 수 없는 상세 보기 항목입니다")
    exchange = result.http
    if section == "request":
        return (exchange.request_body, True) if exchange else ("기록된 HTTP 요청이 없습니다.", False)
    if section == "response":
        if exchange:
            if exchange.response_is_json:
                return exchange.response_json, True
            return exchange.response_text if exchange.response_text is not None else "수신한 응답이 없습니다.", False
        return result.raw_response if result.raw_response is not None else "수신한 응답이 없습니다.", not isinstance(result.raw_response, str)
    if section == "raw":
        return exchange.response_text if exchange and exchange.response_text is not None else "수신한 응답이 없습니다.", False
    return getattr(result, "generated_text" if section == "generated" else "thinking_text") or "이 엔드포인트에서 반환하지 않은 항목입니다.", False


def render_section(result: RoutingResult, section: str, full: bool = False) -> tuple[str, bool, int]:
    value, is_json = section_value(result, section)
    try:
        preview, count = abbreviate(value)
        displayed = value if full else preview
        text = json.dumps(displayed, ensure_ascii=False, indent=2) if is_json else str(displayed)
    except RecursionError:
        # Preserve an unsupported JSON envelope as its original HTTP text.
        value = result.http.response_text if result.http else "응답 중첩이 너무 깊어 형식을 지정할 수 없습니다."
        preview, count = abbreviate(value)
        text, is_json = value if full else preview, False
    return text, is_json, count


def inspect_result(result: RoutingResult, section: str, full: bool = False) -> str:
    return render_section(result, section, full)[0]


def inspector_data(result: RoutingResult) -> dict:
    sections = {}
    for section in SECTIONS:
        preview, is_json, count = render_section(result, section)
        sections[section] = {"preview": preview, "full": inspect_result(result, section, full=True), "omitted": count, "is_json": is_json}
    return sections


def export_result(result: RoutingResult, section: str, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    _, is_json = section_value(result, section)
    path = directory / f"{result.router_name.lower()}-{section}-{uuid4().hex}.{ 'json' if is_json else 'txt'}"
    with path.open("x", encoding="utf-8", errors="backslashreplace") as file:
        file.write(inspect_result(result, section, full=True))
    return path
