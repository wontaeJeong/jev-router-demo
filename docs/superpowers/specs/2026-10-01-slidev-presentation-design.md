# Slidev Jev presentation design

Approved in chat on 2026-10-01. The user subsequently requested starting from
the latest remote commit and merging the completed PR. The isolated branch was
fast-forwarded to `origin/main` at `c64f67a`, which includes the Reveal.js deck.

## Content and scope

Add an independently runnable Slidev presentation to the existing repository.
`presentation/talk.md` is the existing source of truth for content and narrative.
Preserve it and all files inside `presentation/reveal/`. Preserve Python source,
CLI behavior, API contracts, integrations, scenarios and measurement logic.

Create exactly ten slides: Opening, Jev in one sentence, Why this matters,
What Jev returns, Existing approaches, System One + System Two, Agent Router,
What we measure, Live demo and Takeaway. Use Korean-led explanation and the
existing English technical terms. The closing message is “Generate when you
need generation. Decide when you need a decision.”

Use the original durations: 0:40, 1:10, 1:30, 1:30, 1:40, 1:30, 1:30, 1:00,
3:00 and 1:30. These total 14:40; allow twenty seconds for terminal transitions
within the approximately fifteen-minute talk. Durations appear only in notes.

## Package and authoring

`presentation/slidev/` contains `slides.md`, `package.json`, npm lockfile,
`style.css`, two reusable Vue components (`DecisionCard`, `MetricCard`), a local
ignore file and README. Use Slidev 53.0.0 and the default theme with custom
styling. The published CLI requires Node.js >=22.12.0. Verify installed engines
and record them in the README. No separate application scaffold or custom slide
engine is needed.

The Slidev deck is a visual adaptation of the shared original, not an import of
Reveal markup. Notes are concise per-slide cues, not a duplicate full script.
Use standard frontmatter and slide separators, layouts, small declarative HTML
diagrams, UnoCSS where useful, Shiki highlighting for the CLI command, and two
to three meaningful click stages on comparison and architecture slides.
Disable Monaco. Diagrams prioritize legibility over demonstrating Mermaid.

## Design

Dark 16:9 slides, off-white text, cyan for decisions, neutral gray for generation.
Large system-font typography, flat borders, simple lines, substantial negative
space and high contrast. No remote images, fonts, scripts, icon service or API.
Set `fonts.provider: none`; use OS font stacks with explicit fallbacks. No
decorative imagery, excessive gradients, shadows or card/component framework.

Slide 01 is title-only. Slide 02 visibly contrasts State→Text with State→Decision.
Slide 03 explains bounded questions and generation/parse/validation friction.
Slide 04 depicts the conceptual typed/probabilistic contract without fabricated
probabilities. Slide 05 compares roles rather than ranking implementations.
Slide 06 shows complementary decision and generation paths converging on code.
Slide 07 shows the actual router architecture and schema. Slide 08 previews the
actual measurements. Slide 09 is a terminal anchor. Slide 10 is a clean Q&A screen.

## Demo fidelity

The strict actual schema is `model_tier` (lowercase fast/standard/reasoning),
`needs_web` (boolean) and `needs_approval` (boolean). Two adapters receive the
same request and routing policy concurrently. LiteLLM uses POST
`/chat/completions`; Ollama uses POST `/api/generate`, stream=false, format=json.
Both currently generate JSON and share parsing/validation before normalization
and Rich display. The Ollama adapter is a generation fallback, not a native
typed Jev endpoint. Native typed/probabilistic output is explicitly conceptual.

Live cards cover latency, tokens, schema/parsing and routing result. Candidate
confidence is currently unavailable and labelled N/A. No fabricated benchmark
numbers, zero tokens, cost estimates or confidence. Latency includes response
decoding and decision validation; parse time is measured separately. Actual API
usage is observed, and missing data is not zero. Model differences and cold load
prevent causal speed claims. Routing is simulated; no downstream work executes.

The real command is `uv run jev-router-demo` from repository root. Follow the
original Python Utility, vLLM / CUDA Compatibility and Production DB Cleanup
demo cues using r/n/v/o/q. Browser route /9 must survive terminal switching and
advance to /10 using a single arrow. Actual endpoint comparison requires
configured running services; unavailable services must be reported honestly.

## Workflows and documentation

Provide npm install, dev, build, preview, PDF export and PPTX export scripts.
Use Slidev's own export with a locally installed Playwright browser dependency.
Document browser installation, presenter mode, keyboard controls, live demo,
content ownership, project structure and Node requirements.

Document explicit base-path builds for GitHub Pages, including a separate
`/jev-router-demo/slidev/` deployment path to coexist with Reveal. Do not add a
deployment workflow or replace existing Reveal deployment instructions. Update
`presentation/README.md` with parallel entry points and the root README link
description. Neither deck is designated preferred or official.

## Verification and delivery

Run npm installation, development server, production build and export. Inspect
all ten rendered slides at 1920×1080 with screenshots and geometry checks for
text, diagram, code and footer clipping. Check all click stages, notes and next
slide in presenter mode, keyboard navigation, and demo→terminal→takeaway flow.
Inspect PDF page count and output rendering; verify PPTX export if available.
Serve the production build under the documented sub-path and verify local-only
network requests with external traffic blocked, including presenter view.

Re-run the existing Python tests and verify the preserved Reveal build. Review
the diff and intended files, commit, push and create a PR. The user has explicitly
requested merging this PR after completion; merge following required checks.
Verify the default checkout remains main and report actual verification results,
PR URL, run/build/export commands and any concrete limitations.
