"""Presentation-only previews; stored and exported content is never shortened."""

import json
from pathlib import Path
from uuid import uuid4

from jev_router_demo.models import RoutingResult


SECTIONS = {"request": "Request JSON", "response": "Response JSON", "generated": "Generated", "thinking": "Thinking", "raw": "HTTP raw text"}


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
        raise ValueError("Unknown inspector section")
    exchange = result.http
    if section == "request":
        return (exchange.request_body, True) if exchange else ("No HTTP request recorded.", False)
    if section == "response":
        if exchange:
            if exchange.response_is_json:
                return exchange.response_json, True
            return exchange.response_text if exchange.response_text is not None else "No response received.", False
        return result.raw_response if result.raw_response is not None else "No response received.", not isinstance(result.raw_response, str)
    if section == "raw":
        return exchange.response_text if exchange and exchange.response_text is not None else "No response received.", False
    return getattr(result, "generated_text" if section == "generated" else "thinking_text") or "Not returned by this endpoint.", False


def render_section(result: RoutingResult, section: str, full: bool = False) -> tuple[str, bool, int]:
    value, is_json = section_value(result, section)
    try:
        preview, count = abbreviate(value)
        displayed = value if full else preview
        text = json.dumps(displayed, ensure_ascii=False, indent=2) if is_json else str(displayed)
    except RecursionError:
        # Preserve an unsupported JSON envelope as its original HTTP text.
        value = result.http.response_text if result.http else "Response nesting is too deep to format."
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
