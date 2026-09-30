# Router comparison demo design

Approved in chat on 2026-10-01. This document records that approved design.

## Scope
Python 3.12+, uv, Rich, httpx, python-dotenv, pydantic and pytest.
An interactive CLI compares the routing decision layer, never executes downstream
agents, searches, or commands. No server, frontend, database or persistent history.

## Flow
The same full request goes concurrently to LiteLLM `/chat/completions` and Ollama
`/api/generate` with `stream: false`. Each adapter returns a RoutingResult.
Both use the same policy: actual task complexity, current information needs, and
approval for consequential changes (explicit read-only requests do not need approval).
LiteLLM produces JSON. The default Ollama adapter also generates decision JSON;
it is not presented as generation-free or typed. Jev-specific assumptions remain
in `routers/ollama_jev.py`, especially build_jev_prompt and parse_jev_response.
No candidate probabilities are available in the standard Ollama response; token
logprobs are not candidate confidence and are not converted into confidence.

## Measurement
Per-router latency starts immediately before its HTTP call and ends after response
decoding and decision validation. Parse time separately measures decision parsing.
Record actual input/output/total tokens when supplied, and UTF-8 bytes of returned
generated content (including separately returned thinking content). Missing values
remain None, distinct from zero. Accumulated totals report observation coverage.
Requests and errors include failed calls; average latency includes successes only.
Parse failures count only attempted decision parses, not transport failures.

## UI and resilience
Rich prompt commands r/n/p/e/v/o/q, six supplied scenarios, one-line custom request,
four-line request preview, full request and raw response inspection. Wide terminals
use two columns, narrow terminals stack. Spinner signals concurrent network work.
Each backend independently catches explicit HTTP/response/validation failures.
Configuration loads `.env.local` without overriding environment variables; missing
required settings produce readable startup errors. Optional API key means no auth
header when empty. No startup network probe. Route visualization is simulation only.

## Verification
Offline tests cover strict/fenced parsing, invalid values, cumulative metrics,
configuration, adapter payloads, error isolation, concurrency, and UI rendering.
Run uv sync, uv run pytest, and uv run jev-router-demo; actual endpoint accuracy
and performance require configured running models, and cannot be claimed offline.
