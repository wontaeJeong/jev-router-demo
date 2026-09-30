from jev_router_demo.metrics import RouterMetrics
from jev_router_demo.models import RoutingDecision, RoutingResult


def success(latency, **kwargs):
    return RoutingResult(
        "LLM", decision=RoutingDecision(model_tier="fast", needs_web=False, needs_approval=False),
        latency_ms=latency, parse_success=True, **kwargs,
    )


def test_count_success_only_average_observed_sums_and_failures():
    metrics = RouterMetrics()
    metrics.add(success(100, input_tokens=10, output_tokens=0, generated_bytes=50))
    metrics.add(success(300, input_tokens=20, output_tokens=5))
    metrics.add(RoutingResult("LLM", latency_ms=900, parse_success=False, error="invalid JSON", output_tokens=3))
    assert metrics.requests == 3
    assert metrics.successes == 2
    assert metrics.average_latency_ms == 200
    assert metrics.errors == 1
    assert metrics.parse_failures == 1
    assert metrics.parse_attempts == 3
    assert metrics.totals["input_tokens"] == 30
    assert metrics.observations["input_tokens"] == 2
    assert metrics.totals["output_tokens"] == 8
    assert metrics.observations["output_tokens"] == 3
    assert metrics.totals["generated_bytes"] == 50
    assert metrics.observations["generated_bytes"] == 1


def test_no_success_or_usage_remains_unavailable():
    metrics = RouterMetrics()
    assert metrics.average_latency_ms is None
    metrics.add(RoutingResult("JEV", latency_ms=200, error="timeout"))
    assert metrics.average_latency_ms is None
    assert metrics.observations["input_tokens"] == 0
    assert metrics.parse_attempts == 0
    assert metrics.parse_failures == 0


def test_typed_output_has_no_parse_attempt():
    metrics = RouterMetrics()
    metrics.add(success(1, parse_required=False, output_kind="typed"))
    assert metrics.parse_attempts == 0
