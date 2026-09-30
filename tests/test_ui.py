from io import BytesIO, StringIO, TextIOWrapper

import pytest
from rich.console import Console

from jev_router_demo.metrics import RouterMetrics
from jev_router_demo.models import RoutingDecision, RoutingResult
from jev_router_demo.scenarios import SCENARIOS
from jev_router_demo.ui import render_screen, route_line, show_raw_outputs


@pytest.mark.parametrize("width", [60, 120])
def test_result_screen_shows_actual_and_unavailable_metrics(width):
    stream = StringIO()
    console = Console(file=stream, width=width, color_system=None)
    decision = RoutingDecision(model_tier="standard", needs_web=True, needs_approval=True)
    llm = RoutingResult("LLM", decision=decision, latency_ms=20, output_tokens=0, parse_success=True)
    jev = RoutingResult("JEV", latency_ms=5, error="connection refused [not markup]")
    metrics = {"LLM": RouterMetrics(), "JEV": RouterMetrics()}
    for result in [llm, jev]:
        metrics[result.router_name].add(result)
    render_screen(console, SCENARIOS[4], 4, (llm, jev), metrics)
    output = stream.getvalue()
    assert "STANDARD" in output
    # Columns can interleave wrapped lines; assert route semantics separately.
    assert "HUMAN APPROVAL REQUIRED" in route_line(llm)
    assert "HUMAN APPROVAL" in output
    assert "REQUIRED" in output
    assert "WEB ENABLED" in output
    assert "connection refused [not markup]" in output
    assert "Cumulative Metrics" in output
    assert "-" in output
    assert "0" in output
    assert "SIMULATION" in output


def test_route_is_simulation_with_no_approval():
    result = RoutingResult("JEV", decision=RoutingDecision(model_tier="fast", needs_web=False, needs_approval=False))
    assert "FAST MODEL" in route_line(result)
    assert "WEB DISABLED" in route_line(result)
    assert "EXECUTE (SIMULATED)" in route_line(result)


def test_all_scenarios_and_request_preview():
    assert len(SCENARIOS) == 6
    stream = StringIO()
    render_screen(Console(file=stream, width=60, color_system=None), SCENARIOS[5], 5, None, {"LLM": RouterMetrics(), "JEV": RouterMetrics()})
    assert "Scenario 6/6" in stream.getvalue()
    assert "…" in stream.getvalue()
    assert "[v]" in stream.getvalue()


def test_actual_candidate_probabilities_only_when_present():
    stream = StringIO()
    result = RoutingResult("JEV", probabilities={"model_tier": {"REASONING": 0.91, "STANDARD": 0.07, "FAST": 0.02}})
    console = Console(file=stream, width=120, color_system=None)
    metrics = {"LLM": RouterMetrics(), "JEV": RouterMetrics()}
    render_screen(console, SCENARIOS[0], 0, (RoutingResult("LLM"), result), metrics)
    assert "91%" in stream.getvalue()


def test_wide_results_share_a_row_even_with_long_routes():
    stream = StringIO()
    result = RoutingResult("LLM", decision=RoutingDecision(model_tier="reasoning", needs_web=True, needs_approval=True))
    other = RoutingResult("JEV", decision=result.decision)
    render_screen(Console(file=stream, width=120, color_system=None), SCENARIOS[5], 5, (result, other), {"LLM": RouterMetrics(), "JEV": RouterMetrics()})
    assert any("LLM Router" in line and "JEV Router" in line for line in stream.getvalue().splitlines())


def test_raw_inspection_handles_invalid_generated_unicode():
    buffer = BytesIO()
    stream = TextIOWrapper(buffer, encoding="utf-8", errors="strict")
    console = Console(file=stream, width=120, color_system=None)
    result = RoutingResult("LLM", generated_text="\ud800", raw_response={"content": "\ud800"})
    show_raw_outputs(console, (result, RoutingResult("JEV")))
    stream.flush()
    assert b"\\ud800" in buffer.getvalue()
