# Jev Presentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Inline execution was selected for this session.

**Goal:** Build a ten-slide offline-first Reveal.js deck supporting a 15-minute talk and the existing CLI live demo.

**Architecture:** One Markdown source is imported by Vite into Reveal's Markdown plugin. Semantic HTML diagrams live in that source; layout lives in a single CSS theme. The CLI stays independent.

**Tech Stack:** Reveal.js, Vite, vanilla JavaScript, CSS, Markdown, npm.

**Spec:** `docs/superpowers/specs/2026-10-01-jev-presentation-design.md`

## Global Constraints

- Exactly ten horizontal slides, Korean-led content, 1600 × 900 logical dimensions.
- System fonts only; no remote runtime assets or APIs.
- Current Ollama adapter is a generation fallback; confidence is unavailable.
- No CLI changes; no fabricated probabilities or benchmark metrics.
- Closing: “Generate when you need generation. Decide when you need a decision.”
- Static production assets must support arbitrary deployment subpaths.

### Task 1: Content and slide runtime

**Files:** Create `presentation/talk.md`, `presentation/reveal/index.html`,
`presentation/reveal/package.json`, `presentation/reveal/package-lock.json`,
`presentation/reveal/vite.config.js`, `presentation/reveal/src/main.js`,
`presentation/reveal/src/theme.css`, `presentation/reveal/.gitignore`.

**Interfaces:** main.js imports `../../talk.md?raw`; Markdown delimiters are
`---` and `Note:`. Each slide has a named id and data-timing attribute. The
initialized Reveal instance is exposed as `window.Reveal` for speaker view.

- [x] Write ten slides matching the spec, using classed semantic diagrams for
  comparisons, output flow, landscape, architecture, router and metrics.
- [x] Add time/key point/transition cues in every Note block; put real demo
  scenario details and command in slides 7–9 notes.
- [x] Create npm scripts `dev: vite --host 127.0.0.1`, `build: vite build`,
  `preview: vite preview --host 127.0.0.1`; use `base: './'` in Vite config.
- [x] Import Reveal, Markdown, Highlight and Notes from local npm modules.
  Populate a textarea data-template using textContent, then initialize with
  `hash: true`, `slideNumber: 'c/t'`, `progress: true`, `transition: 'fade'`,
  `pdfSeparateFragments: false`, `pdfMaxPagesPerSlide: 1`, `view: 'slide'`.
- [x] Style fixed logical slides with generous margins, large system-font
  typography, cyan decision paths, aligned grids and reserved footer space.
- [x] Run `npm install` and `npm run build` in presentation/reveal; launch dev
  and preview on 5173 and 4173. Inspect installed Notes source for remote
  assets and bundle a local speaker view if its default loader requires one.

### Task 2: Documentation and browser acceptance

**Files:** Create `presentation/README.md`; update root `README.md` with link.

**Interfaces:** README commands run inside presentation/reveal; CLI commands
run from repository root. Production output is presentation/reveal/dist/.

- [x] Document npm install/dev/build/preview, content ownership, S/F/arrows,
  demo and takeaway hashes, existing CLI configuration and r/n/o/q cues.
- [x] Document `?print-pdf`, Chrome Save as PDF, landscape, no margins,
  backgrounds, ten pages, and static deployment of the whole dist directory.
- [x] Open all slides in dev and preview at 1920×1080 and 1366×768; capture
  screenshots and check rendered text, diagrams and element bounds.
- [x] Verify fragments on slide 6; keyboard navigation; direct demo hash and
  refresh; terminal round-trip and one-step advance to takeaway; numbers and
  progress; S speaker popup and all ten notes.
- [x] Export Chromium PDF with printBackground and preferCSSPageSize, inspect
  ten pages and clipped text; request only local assets for deck and notes.
- [x] Serve dist under /jev-router-demo/ and verify deck, notes and hashes.
- [x] Fix any discovered defect and rerun the relevant acceptance checks.

### Task 3: Review and delivery

**Files:** Only planned presentation and documentation files.

- [ ] Inspect `git diff --check`, status, full diff and recent log; review
  content against CLI and the ten-slide quality bar.
- [x] Run final production build; record actual browser verification results.
- [ ] Commit intended files, push feat/jev-presentation and create a PR using
  gh with scope and evidence. Return PR URL and ask for merge approval.
- [ ] Verify base checkout remains main and worktree branch mapping is intact.

## Verification record

- Baseline CLI tests: 47 passed; no CLI code changes.
- npm install: success, 0 audit vulnerabilities. Vite 8.3.1 / Reveal 5.2.1.
- Production build: success; Vite reports a non-blocking large-bundle warning
  for the bundled syntax highlighter (368 kB gzip JavaScript).
- Ten slides checked in dev and production; final production bounds and footer
  checks passed at 1920×1080 and 1366×768.
- S speaker popup synchronized all ten notes under /jev-router-demo/; no remote
  requests from presentation or speaker view.
- Keyboard fragments 0 → 1 → 2; F fullscreen; named hashes/reload; demo focus
  round-trip and one-step Space advance to takeaway verified.
- Chromium PDF exported ten pages with both fragments visible, dark backgrounds
  and no content outside page bounds. Generated PDF remains a local artifact.
- Read-only code review: no critical/important findings. Minor token availability
  wording was verified against ui.py and corrected in the notes.
