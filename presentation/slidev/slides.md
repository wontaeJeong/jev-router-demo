---
theme: default
title: Jev — Decision Models for Agentic Systems
info: |
  15분 발표 · presentation/talk.md의 독립 Slidev adaptation.
  실제 Agent Router CLI는 terminal에서 실행합니다.
author: Jev Router Demo
favicon: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"%3E%3Crect width="32" height="32" fill="%23101820"/%3E%3Cpath d="M21 7v13a6 6 0 0 1-12 0" fill="none" stroke="%2360d8e5" stroke-width="4"/%3E%3C/svg%3E'
colorSchema: dark
aspectRatio: 16/9
canvasWidth: 1280
presenter: true
monaco: false
download: false
transition: fade
fonts:
  provider: none
  sans: 'system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
  mono: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'
drawings:
  persist: false
layout: cover
class: opening
---

<div class="eyebrow">DECISION MODELS FOR AGENTIC SYSTEMS</div>

# Jev

<div class="opening-subtitle">Decision Models<br>for Agentic Systems</div>
<div class="opening-caption muted">Not everything needs to be a generation.</div>

<!--
0:40 · Opening
- 질문: Agent가 해야 하는 모든 판단을 Generative LLM에게 맡겨야 할까?
- 모델 선택·도구 사용·승인처럼 작은 판단을 오늘의 대상으로 삼는다.
- Jev 개념 → 기존 CLI demo. 전환: “글을 쓰는 AI와 보기 중 판단하는 AI를 나눠 보겠습니다.”
-->

---
layout: default
---

<div class="eyebrow">02 / THE IDEA</div>

## 글을 생성하는 것, 판단하는 것

<div class="comparison">
  <article class="compare-side" v-click="1">
    <div class="label">GENERATIVE LLM</div>
    <h3>“글을 써주는 AI”</h3>
    <div class="short-flow"><span>STATE</span><span class="arrow">↓</span><strong>TEXT</strong></div>
  </article>
  <article class="compare-side decision" v-click="2">
    <div class="label">JEV / DECISION MODEL</div>
    <h3>“보기 중에서 판단하는 AI”</h3>
    <div class="short-flow"><span>STATE</span><span class="arrow">↓</span><strong>DECISION</strong></div>
  </article>
</div>

<div class="key-message" v-click="3">Unstructured state in.<br><span class="accent">Typed probabilistic decisions out.</span></div>

<!--
1:10 · Jev in one sentence
- Click 1: State→Text. Click 2: State→Decision. Click 3: 입력은 자유롭고 출력 공간은 정해진다.
- Jev의 차이는 크기보다 interface와 역할. Boolean·score도 “보기”에 포함된다.
- 판단 뒤에는 code가 이어진다. 전환: “지금 Agent는 작은 판단도 generation으로 처리하곤 합니다.”
-->

---
layout: default
---

<div class="eyebrow">03 / THE FRICTION</div>

## 작은 판단에 긴 우회로

<div class="problem-layout">
  <div class="questions">
    <p>빠른 모델이면 될까?</p>
    <p>웹 검색이 필요할까?</p>
    <p>승인을 받아야 할까?</p>
    <p>결과가 충분히 좋을까?</p>
    <p>다시 시도해야 할까?</p>
  </div>
  <div class="generation-pipeline">
    <div>Request → Large LLM</div>
    <div class="arrow">↓</div>
    <div>Generated text</div>
    <div class="arrow">↓</div>
    <div>Parse → Validate → Retry?</div>
    <div class="arrow">↓</div>
    <strong>Branch</strong>
  </div>
</div>

<div class="key-message">이미 한정된 판단에 <span class="accent">generation</span>을 쓰고 있다.</div>
<div class="cost-strip muted">Latency <span>·</span> Tokens <span>·</span> Parsing <span>·</span> Validation <span>·</span> Retries</div>

<!--
1:30 · Why this matters
- 질문은 bounded인데 code까지 생성·파싱·검증 경로가 필요하다.
- Structured output은 형식을 안정화할 수 있다. Typed probabilistic decision과는 다른 계약이다.
- Retry?는 일반 패턴이며 실제 CLI에는 자동 retry가 없다. 수치 우위를 주장하지 않는다.
- 전환: “처음부터 질문과 답의 타입을 정의한다면 어떨까요?”
-->

---
layout: default
---

<div class="eyebrow">04 / THE CONTRACT <span class="tag">CONCEPT · 측정값 아님</span></div>

## 텍스트 대신, 판단의 계약

<div class="contract-flow">
  <div class="state-column">
    <div class="label">STATE</div>
    <div>User request</div><div>Agent context</div><div>Tool state</div><div>Previous results</div>
  </div>
  <div class="arrow accent">→</div>
  <div class="decision-stack">
    <DecisionCard label="model_tier?" value="fast" detail="Choice · fast / standard / reasoning" />
    <DecisionCard label="needs_web?" value="false" detail="Boolean · 명시적인 타입" />
    <DecisionCard label="needs_approval?" value="false" detail="Boolean · 명시적인 타입" />
  </div>
</div>

<div class="contract-principles"><span>Predefined questions.</span><span>Typed answers.</span><span class="accent">Explicit P(candidate).</span></div>
<div class="footnote">확률은 계약의 일부. 수치는 생략하며 현재 CLI의 응답 예시가 아닙니다.</div>

<!--
1:30 · What Jev returns
- Concept: state→미리 정의된 질문→typed decisions + 후보별 확률→code.
- Choice/Boolean은 일반 타입 명칭이다. 공식 Jev SDK/API를 가정하지 않는다.
- Confidence threshold를 code의 분기에 사용할 수 있다. 숫자를 만들어 보여주지 않는다.
- 현재 Ollama fallback은 JSON 생성·parse, probability 미제공. 전환: “기존 접근과 목적을 비교해 보겠습니다.”
-->

---
layout: default
---

<div class="eyebrow">05 / THE LANDSCAPE</div>

## 우열보다, 목적의 차이

| Approach | 주된 역할 | 판단의 표현 |
| --- | --- | --- |
| Rule / heuristic | 명시적 조건으로 분기 | 조건 → 값 |
| Traditional classifier | 학습한 label로 분류 | Label / probability |
| LLM + structured output | 형식을 제한한 생성 | Generated JSON |
| LLM judge | 내용을 평가·비교 | 평가 / 점수 생성 |
| Guard / policy model | 허용 여부를 판정 | Policy verdict |
| **Jev / Decision Model** | **State의 bounded decision** | **Typed / probabilistic** |

<div class="key-message">선택 기준은 <span class="accent">어떤 출력을 필요로 하는가.</span></div>

<!--
1:40 · Existing approaches
- 순위표가 아니다. Classifier도 typed label과 확률을 제공할 수 있다.
- Structured output은 형식, judge는 평가, guard는 policy에 초점. 구현은 서로 겹친다.
- Decision Model은 여러 predefined questions와 typed/probabilistic interface를 중심에 둔다.
- 전환: “이 판단 계층을 Agent 전체에 어떻게 배치할까요?”
-->

---
layout: default
---

<div class="eyebrow">06 / THE ARCHITECTURE</div>

## System One + System Two

<div class="agent-head"><strong>AGENT</strong><span class="muted">지금 필요한 것은 판단인가, 생성인가?</span></div>
<div class="system-paths">
  <article class="system decision" v-click="2">
    <div class="path-arrow">↓</div>
    <div class="label">SYSTEM ONE · DECIDE</div>
    <h3>Decision Model</h3>
    <p>route · classify · gate<br>score · judge · triage</p>
    <div class="muted">한정된 판단 공간</div>
  </article>
  <article class="system" v-click="1">
    <div class="path-arrow">↓</div>
    <div class="label">SYSTEM TWO · GENERATE</div>
    <h3>Generative LLM</h3>
    <p>reason · write · code<br>plan · summarize</p>
    <div class="muted">열린 생성 공간</div>
  </article>
</div>
<div v-click="3" class="merge-destination"><span>↓</span><strong class="mono">DETERMINISTIC CODE</strong><span>↓</span></div>
<div class="key-message" v-click="3">필요한 곳에 생성. <span class="accent">한정된 곳에 판단.</span></div>

<!--
1:30 · System One + System Two
- 처음: Agent 질문. Click 1: 기존 generation 경로. Click 2: bounded decision 경로 추가.
- Click 3: code에서 결합. 실제 동작과 상태 변경은 code가 담당한다.
- System One/Two는 역할의 비유. Jev는 Generative LLM 전체의 대체재가 아니다.
- 전환: “이 중 route에 집중한 CLI를 보겠습니다.”
-->

---
layout: default
---

<div class="eyebrow">07 / THE DEMO</div>

## Agent Router: 같은 입력, 같은 schema

<div class="schema-strip mono"><div>model_tier<strong>fast / standard / reasoning</strong></div><div>needs_web<strong>true / false</strong></div><div>needs_approval<strong>true / false</strong></div></div>
<div class="shared-request">SAME FULL REQUEST</div>
<div class="router-paths">
  <article><div class="arrow">↓</div><h3>LLM Router</h3><div class="muted">LiteLLM</div><code>POST /chat/completions</code><div class="output-label">Generated JSON</div></article>
  <article class="decision"><div class="arrow">↓</div><h3>Jev-like Router</h3><div class="muted">Ollama · generation fallback</div><code>POST /api/generate</code><div class="output-label">Generated JSON</div></article>
</div>
<div class="shared-result">↓ &nbsp; Parse / validate → RoutingDecision → CLI 비교</div>
<div class="footnote">현재 두 경로 모두 generation. Routing은 표시만 하며 downstream 작업은 실행하지 않습니다.</div>

<!--
1:30 · Agent Router
- Same full request, routing policy, strict schema. model_tier 실제 값은 lowercase.
- LiteLLM /chat/completions, Ollama /api/generate (stream=false, format=json).
- Jev-like도 JSON 생성·parse. Native typed Jev endpoint의 성능 비교가 아니다.
- 동일 normalized result/UI, 실제 웹 검색·DB 변경 없음. Python Utility→vLLM/CUDA→DB Cleanup scenario 활용.
- 전환: “무엇을 실제로 관측할 수 있을까요?”
-->

---
layout: default
---

<div class="eyebrow">08 / WHAT TO WATCH</div>

## 숫자는 지금, 터미널에서

<div class="metrics-grid">
  <MetricCard label="LATENCY" detail="응답 + parsing / validation" />
  <MetricCard label="TOKENS" detail="실제 input / output usage" />
  <MetricCard label="SCHEMA / PARSING" detail="성공 여부 · parse time" />
  <MetricCard label="ROUTING RESULT" detail="Tier · Web · Approval" />
</div>
<div class="confidence-strip"><span class="label">DECISION CONFIDENCE</span><strong>N/A</strong><span class="muted">현재 endpoint 미제공</span></div>
<div class="key-message">같은 판단인가? <span class="accent">어떤 비용으로 얻었는가?</span></div>
<div class="footnote">모델·cold load·출력 차이도 latency에 영향을 줍니다. “—”는 0이 아니라 미관측.</div>

<!--
1:00 · What we measure
- Latency: 개별 HTTP 호출 직전부터 decoding + validation까지. 다른 Router 대기 시간 제외.
- Tokens: 실제 API usage. Ollama total은 input+output 합. 미제공은 0이 아니다.
- Parse time/성공, route 비교. Confidence는 없어 UI에서 생략. Token logprobs와 혼동하지 않는다.
- 모델/cold load 차이 때문에 방식만의 인과적 benchmark가 아니다. 전환: “터미널로 가겠습니다.”
-->

---
layout: default
class: live-demo
---

<div class="eyebrow">09 / SWITCH TO TERMINAL</div>

# LIVE DEMO

<div class="demo-statement">Same request.<br>Same decisions.<br><span class="accent">Compare the decision paths.</span></div>

```bash
uv run jev-router-demo
```

<div class="demo-workflow muted">Scenario → Both routers → Compare</div>
<div class="footnote">Repository root에서 실행 · 브라우저 복귀 후 → 한 번으로 Takeaway</div>

<!--
3:00 · Live demo
- Terminal 전환 → repo root에서 uv run jev-router-demo (.env.local, LiteLLM/Ollama 사전 준비).
- Python Utility: r + Enter. 같은 input, 두 Router의 Tier/Web/Approval 확인.
- n 두 번 → vLLM / CUDA Compatibility → r: needs_web. n 두 번 → Production DB Cleanup → r: needs_approval.
- 각 결과의 latency·input/output tokens·parse 비교. 여유 있으면 o → raw output → Enter 복귀.
- Confidence 현재 미제공. 연결 실패하면 실제 오류를 설명하고 다른 panel 확인.
- q → browser /9 복귀 → 오른쪽 화살표 한 번 → /10. 실제 downstream 작업은 실행되지 않는다.
- 복귀: “숫자보다 중요한 것은 생성과 판단의 역할 분리입니다.”
-->

---
layout: end
class: takeaway
---

<div class="eyebrow">10 / TAKEAWAY</div>

<div class="takeaway-line">Generate when you<br>need generation.</div>
<div class="takeaway-line accent">Decide when you<br>need a decision.</div>
<div class="complement">Generative LLM <span class="accent">+</span> Decision Model</div>
<div class="closing-line muted">Not everything needs to be a generation.</div>

<!--
1:30 · Takeaway / Q&A anchor
- Demo는 현재 두 경로 모두 generated JSON. Native typed/probabilistic 계약과 관측 기준을 분리했다.
- Write/code/reason/plan에는 생성. Bounded route/gate/score에는 Decision Model 고려.
- 둘은 보완 관계, 실제 실행은 code. 핵심 두 문장을 읽고 마무리.
- Q&A 동안 이 화면 유지. Notes 시간 합계 15:00, terminal 전환은 Live demo 3:00에 포함.
-->
