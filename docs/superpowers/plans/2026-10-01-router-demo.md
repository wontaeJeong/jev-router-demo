# Jev Router Demo Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Build the approved small interactive routing comparison demo.

**Architecture:** Independent LiteLLM and Ollama adapters normalize actual HTTP responses into RoutingResult. Concurrent orchestration feeds Rich presentation and in-memory metrics. No downstream execution.

**Tech Stack:** Python 3.12+, uv, Rich, httpx, python-dotenv, pydantic, pytest.

**Spec:** docs/superpowers/specs/2026-10-01-router-demo-design.md

## Global Constraints
- Python 3.12+; no web server, frontend, Textual, database or persistent history.
- Same full request, concurrent calls, independent measured latency.
- Missing measurements are None; no fabricated metrics or confidence.
- Standard Ollama generation is labeled generated, with parsing and actual counts.
- Jev contract changes stay in routers/ollama_jev.py.
- Default checkout stays on main; all work in the isolated worktree.

## Task 1: Bootstrap, validation and configuration
Files: pyproject.toml, .gitignore, .env.example, src/jev_router_demo/{__init__,models,config,scenarios}.py; tests/test_parsing.py, tests/test_config.py.
Interfaces: load_config() -> Config; parse_decision(text: str) -> RoutingDecision; SCENARIOS: list[Scenario]. RoutingResult stores optional metrics, decision, raw response and error.
- [x] Add packaging with console script `jev-router-demo = jev_router_demo.main:main` and uv dev pytest dependency.
- [x] Add failing cases: strict JSON, fenced JSON, invalid tier, string booleans, extra fields; dotenv override precedence and missing settings.
- [x] Run `uv sync` then `uv run pytest tests/test_parsing.py tests/test_config.py`; expect missing-module failure before implementing modules.
- [x] Implement strict pydantic decision validation, dataclass result/config, and six exact user requests with expected metadata.
- [x] Re-run focused tests, expecting all cases to pass.

## Task 2: HTTP adapters and concurrent routing
Files: src/jev_router_demo/routers/{__init__,litellm,ollama_jev}.py, src/jev_router_demo/main.py; tests/test_routers.py.
Interfaces: each router has `async route(request: str) -> RoutingResult`; `async compare(request: str, llm: LiteLLMRouter, jev: OllamaJevRouter) -> tuple[RoutingResult, RoutingResult]`; build_jev_prompt(request: str) -> str; parse_jev_response(response: dict[str, object]) -> RoutingResult.
- [x] Write httpx.MockTransport tests asserting original user content and Ollama prompt inclusion, optional authorization, measured metrics, invalid envelopes, HTTP errors and independent failure handling.
- [x] Prove concurrency with an asyncio Event barrier in transport handlers: both handlers must enter before either completes, guarded with wait_for.
- [x] Run `uv run pytest tests/test_routers.py` and confirm missing implementations fail.
- [x] Implement standard HTTP payloads, shared routing policy, strict envelope parsing and explicit exception handling. Retain response and usage when decision parsing fails. Time each call separately.
- [x] Run adapter tests; verify generation and thinking bytes and None/zero distinction.

## Task 3: Metrics
Files: src/jev_router_demo/metrics.py, tests/test_metrics.py.
Interfaces: RouterMetrics.add(result: RoutingResult) -> None; average_latency_ms -> float | None; totals and observation counts for optional numeric metrics.
- [x] Write tests with successes of 100 and 300 ms plus a failed 900 ms call: requests 3, errors 1, average 200 ms. Supply zero and missing usage values to test coverage.
- [x] Run focused test before implementation and confirm failure.
- [x] Implement successful-only latency average, observed totals, parse-attempt/failure counts, and error counts.
- [x] Re-run focused tests and confirm expected totals.

## Task 4: CLI, documentation and verification
Files: src/jev_router_demo/{main,__main__,ui}.py, README.md; tests/test_ui.py.
Interfaces: UI consumes only normalized models and metrics; main() loads config and runs async interactive loop with one reused AsyncClient.
- [x] Implement Rich title, truncated request panel, two-column/stacked result panels, route simulation, cumulative totals with coverage, spinner, raw JSON/text inspection and prompt commands.
- [x] Add rendering tests at 60 and 120 columns with unavailable values and approval routes; use plain text rendering to avoid markup interpretation of model output.
- [x] Document uv sync/config/run, endpoints, measurement boundaries, cold-start effects, generated Ollama fallback and exact future adapter customization points.
- [x] Run `uv sync`, `uv run pytest`, `uv run jev-router-demo` with missing configuration, then configured command-input smoke tests with unavailable localhost endpoints.
- [x] Review diff and dependencies for prohibited features, invented metrics and backend JSON leaking into UI.
- [ ] Report actual verification and workspace location. Commit/push/PR only when permitted by applicable instructions.

## Verification record
2026-10-01: uv sync succeeded; uv run pytest passed 47 tests; compileall passed.
Console entrypoint reports missing configuration without traceback (exit 1).
Configured console entrypoint smoke test exercised next/previous, custom input,
real localhost connection failures, raw inspection and quit (exit 0).
Code review findings for fixed-width layout, invalid Unicode isolation and
malformed URL ports were reproduced, fixed and verified by regression tests.
No actual local model endpoints were configured; real model accuracy/latency
remain to be measured with the presenter's .env.local and running endpoints.
