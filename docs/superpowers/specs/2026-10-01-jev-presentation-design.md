# Jev presentation design

> Historical design, superseded on 2026-10-06 by the approved Slidev-only refinement.
> Reveal.js and the shared talk source were removed. Current content and workflows:
> `presentation/slidev/slides.md` and `presentation/README.md`.

Approved in chat on 2026-10-01 after repository investigation.

## Content and scope

A presentation-first, Korean-led 15-minute deck with exactly ten horizontal
slides: Opening, Jev in one sentence, Why this matters, What Jev returns,
Existing approaches, System One + System Two, Agent Router, What we measure,
Live demo, Takeaway. The closing message is “Generate when you need generation.
Decide when you need a decision.” Jev handles bounded decisions and complements
generation; it does not replace the whole agent.

No existing talk.md or presentation assets were found. `presentation/talk.md`
becomes the single presentation source, including concise speaker notes and
recommended durations (40, 70, 90, 90, 100, 90, 90, 60, 180, 90 seconds).
Markdown contains semantic HTML only where a diagram requires layout.

## Implementation

`presentation/reveal/` contains Reveal.js, Vite, vanilla JS and CSS, with npm
install/dev/build/preview workflows and a lockfile. Vite imports talk.md as raw
text into Reveal's Markdown plugin. There is no duplicate HTML slide content.
Markdown, highlighting and speaker-notes plugins are bundled locally.
Use 1600 × 900 logical dimensions, fade transitions, keyboard navigation, named
URL hashes, slide numbers and progress. PDF prints one page per slide with all
fragments visible. Assets use relative paths for arbitrary static subpaths.

## Visual direction

Dark navy, off-white, one cyan accent for decisions. Neutral gray represents
generation. System fonts only. Large headings, minimal labels, flat borders,
generous negative space and semantic grid/flex diagrams. No images, external
fonts, frameworks, backend, CMS or decorative animation. Only two reveal stages
on the architecture slide. Keep footer and controls clear of slide content.

## Demo fidelity

Existing CLI is unchanged. `uv run jev-router-demo` runs from the repository
root. Both adapters use the same RoutingDecision schema (fast/standard/reasoning,
needs_web, needs_approval). LiteLLM POST /chat/completions and Ollama POST
/api/generate currently produce generated JSON that is parsed and validated.
The current Ollama adapter is a Jev-like generation fallback, not a typed
decision endpoint. Candidate confidence is unavailable. Routing is displayed,
not executed downstream.

Slide 4 shows conceptual typed probabilistic output without invented measured
probabilities. Slides 7–8 label the actual fallback, show LIVE for observable
metrics and N/A for confidence. Notes explain cold load/model differences and
avoid causal benchmark claims. Use the shipped Python Utility, vLLM / CUDA
Compatibility and Production DB Cleanup scenarios as demo cues. Slide 9 anchors
terminal switching; slide 10 remains usable for Q&A.

## Documentation and verification

Presentation README documents npm workflows, S speaker view, F fullscreen,
arrows/space, named demo/takeaway hashes, PDF printing with backgrounds and
deployment of dist/ to static hosting including GitHub Pages. Root README links
to it. No Pages workflow is needed.

Verify build and dev/production rendering, all ten slides at notebook and 1080p
sizes, clipping/diagrams, fragments, hashes, progress/numbers, S speaker popup
and notes sync, demo-to-takeaway navigation, PDF ten-page output and local-only
requests including speaker view. Check production under a repository subpath.
Existing CLI baseline: 47 tests passed before changes.
