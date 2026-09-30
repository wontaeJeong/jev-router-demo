from dataclasses import dataclass, field

from jev_router_demo.models import RoutingResult


MEASUREMENTS = ("input_tokens", "output_tokens", "total_tokens", "generated_bytes")


@dataclass
class RouterMetrics:
    requests: int = 0
    successes: int = 0
    errors: int = 0
    parse_attempts: int = 0
    parse_failures: int = 0
    successful_latency_ms: float = 0
    totals: dict[str, int] = field(default_factory=lambda: dict.fromkeys(MEASUREMENTS, 0))
    observations: dict[str, int] = field(default_factory=lambda: dict.fromkeys(MEASUREMENTS, 0))

    def add(self, result: RoutingResult) -> None:
        self.requests += 1
        # Failures count toward requests/usage, never toward average latency.
        if result.error is None and result.decision is not None:
            self.successes += 1
            self.successful_latency_ms += result.latency_ms
        else:
            self.errors += 1
        if result.parse_required and result.parse_success is not None:
            self.parse_attempts += 1
            if not result.parse_success:
                self.parse_failures += 1
        for name in MEASUREMENTS:
            value = getattr(result, name)
            if value is not None:
                self.totals[name] += value
                self.observations[name] += 1

    @property
    def average_latency_ms(self) -> float | None:
        return self.successful_latency_ms / self.successes if self.successes else None
