# Slidev Jev Presentation Implementation Plan

> Historical plan, superseded on 2026-10-06 by the approved Slidev-only refinement.
> Do not execute this plan against the current repository; see `presentation/README.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Inline execution follows the user's instruction to start and complete the work in this session. Steps use checkbox syntax for tracking.

**Goal:** Add an independent ten-slide Slidev adaptation of the existing Jev talk, verify it, and merge its PR.

**Architecture:** `presentation/talk.md` remains the content source of truth. Slidev has a separate Markdown visual deck, two small Vue components and a CSS visual system. The Python CLI and Reveal runtime remain independent.

**Tech Stack:** Slidev 53.0.0, default theme, Vue, UnoCSS, Shiki, npm, Playwright export.

**Spec:** `docs/superpowers/specs/2026-10-01-slidev-presentation-design.md`

## Global Constraints

- Node.js >=22.12.0; verify installed package engines.
- Exactly ten slides, 16:9, Korean-led, notes only for durations (15:00 with terminal transitions included in the 3:00 demo).
- Preserve `presentation/talk.md`, `presentation/reveal/` and all Python source/tests.
- Both actual adapters generate JSON. Confidence is unavailable. No fabricated metrics.
- Fonts provider none; no runtime remote assets; Monaco disabled.
- Terminal command `uv run jev-router-demo` runs from repository root.
- Generate when you need generation. Decide when you need a decision.

### Task 1: Independent presentation package

**Files:** Create `presentation/slidev/{package.json,package-lock.json,.gitignore,slides.md,style.css,components/DecisionCard.vue,components/MetricCard.vue}`.

**Interfaces:** `DecisionCard` accepts string `label`, `value`, `detail`; `MetricCard` accepts string `label`, `detail`, and string `value` defaulting to LIVE. Slidev auto-discovers components and `style.css`. Slides use numeric routes /1 through /10.

- [x] Create package with scripts `dev: slidev --open`, `build: slidev build --router-mode hash`, `preview: vite preview --host 127.0.0.1`, `export: slidev export --output exports/jev.pdf --dark --with-clicks false`, `export:pptx: slidev export --format pptx --output exports/jev.pptx --dark --with-clicks false`, `browser:install: playwright install chromium`. Add Slidev CLI/default theme and playwright-chromium.
- [x] Write frontmatter with theme default, colorSchema dark, aspectRatio 16/9, canvasWidth 1280, fonts provider none, presenter true and monaco false. Use cover/end layouts for title/takeaway and default layouts for the other eight.
- [x] Write ten short slides adapting the original story. Slides 2/6 use v-click stages; slides 4/8 use the components; slide 7 shows actual JSON endpoints and lowercase schema. Keep slide 9's command in a bash fence for Shiki.
- [x] Write simple component markup with flat cards. Define typography, comparisons, architecture connectors, schema strip, landscape table and metric grid in CSS. Keep all slide text comfortably within 1280×720 with footer clearance.
- [x] Install with `npm install`, inspect installed engines, run `npm run build`, start `npm run dev -- --port 3030` and inspect first rendered slide. Slidev's dev server defaults to loopback; its CLI does not accept Vite's --host option.

### Task 2: Documentation and browser/export acceptance

**Files:** Create `presentation/slidev/README.md`; update `presentation/README.md` and root `README.md` presentation description. Do not rewrite existing Reveal instructions.

**Interfaces:** Build outputs slidev/dist. PDF/PPTX outputs slidev/exports (ignored). Production base path is passed through CLI `npm run build -- --base /jev-router-demo/slidev/`. Presenter uses /presenter/1; terminal anchor /9; takeaway /10.

- [x] Document install/dev/build/preview, presenter, browser install, PDF/PPTX export, real CLI configuration, exact scenario controls, content ownership and base-path deployment.
- [x] Open slides 1–10 at 1920×1080. Inspect screenshots and content bounds. Check complete click states on slides 2/6, next/previous navigation, code highlighting and notes.
- [x] Open presenter view, check current/next/notes/timer, keyboard navigation and synchronization. From slide 9 run the actual CLI in terminal and return to browser, then one arrow to slide 10. Report unavailable endpoints truthfully.
- [x] Run `npm run export` and `npm run export:pptx`; inspect page count and rendered PDF for text/diagram/background clipping. Export without separate click pages.
- [x] Run sub-path build, preview it at /jev-router-demo/slidev/, block external browser requests and inspect network log for local-only deck/presenter operation. Test direct /9 refresh and /10 navigation.
- [x] Run `uv run pytest` from repo root and `npm ci && npm run build` in presentation/reveal. Verify original talk/reveal source diff is empty.

### Task 3: Review and merge

**Files:** Only new Slidev package, design/plan docs and the two README updates.

- [x] Review the full diff against spec, original source and ten-slide readability criteria. Run git diff --check, git status and git log --oneline -10.
- [ ] Stage intended files, commit, push feat/slidev-presentation. Inspect remote tracking and origin/main..HEAD diff and all included commits, then create a gh PR with actual verification evidence.
- [ ] Inspect PR checks and mergeability; merge with gh after required checks. The user has already explicitly approved this PR's merge.
- [ ] Verify default checkout remains main and worktree mapping, update main safely to origin/main if clean, and report PR URL and actual run/build/export/verification results.

## Verification evidence

- Node 24.21.0 execution via temporary npm node binary; CLI engines >=22.12.0.
- npm install and clean npm ci succeeded. npm audit reports 13 upstream dependency
  findings (2 low, 1 moderate, 10 high). Kept current Slidev rather than downgrade
  the framework or force dependency changes unrelated to this deck.
- Slidev dev at 3030: all ten screenshots reviewed at 1920×1080, zero element
  overflow. Meaningful slides 2/6 have exactly three click stages. The summary on
  slide 6 uses explicit v-click=3 rather than implicit v-after.
- Tooltip console error traced to floating-vue 5.4's changed component internals;
  compatible 5.2.2 override removed the error. Default remote favicon replaced
  with an inline SVG after offline network inspection exposed its CDN request.
- Root production build succeeded; sub-path build and preview at 4180 succeeded.
  External requests blocked: 63 local requests, zero external requests, zero HTTP
  failures, zero page errors across slides/presenter. Final slide 4/10 updates
  were reloaded and visually inspected after rebuilding.
- Presenter: all ten notes, Current/Next, timer start, navigation, and same-origin
  two-tab sync verified. Audience sync adds ?clicks=0 to its URL.
- Live transition: browser /9 → real CLI r/q → browser → one arrow /10 verified.
  Used example local endpoint settings with a two-second timeout. Both endpoints
  refused connections; CLI displayed actual errors and exited 0. Successful
  live routing/token comparison is NOT verified. No fake response was used.
- PDF: ten 16:9 pages, all text bounds inside page; all pages visually inspected
  from rendered PDF contact sheet. PPTX: ten image slides, ten notes; live demo
  note present. Final style correction preserved stacked takeaway typography.
- Existing CLI tests: 47 passed. Reveal npm ci/build succeeded. Source diff for
  talk.md, Reveal, Python source and tests against origin/main is empty.
- Independent read-only review found no Critical/Important issues; corrected a
  mistaken duration total in docs/notes after verifying the sum is 900 seconds.
