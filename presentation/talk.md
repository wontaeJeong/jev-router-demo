<!-- .slide: id="opening" class="opening" data-timing="40" -->

<p class="eyebrow">DECISION MODELS FOR AGENTIC SYSTEMS</p>

# Jev

<p class="opening-line">Not everything needs<br>to be a generation.</p>
<p class="opening-caption">작은 판단에도, 큰 생성이 필요할까?</p>

Note:
**0:40 · Opening**
- Agent는 글을 쓰는 것 외에도 계속 작은 판단을 한다. 모델 선택, 도구 사용, 승인 여부가 그 예다.
- 오늘은 Jev / Decision Model의 관점을 설명하고, 마지막에 기존 CLI Agent Router를 직접 실행한다.
- 전환: “글을 써주는 AI와, 보기 중에서 판단하는 AI를 나눠 보겠습니다.”

---

<!-- .slide: id="one-sentence" data-timing="70" -->

<p class="eyebrow">01 / THE IDEA</p>

## 글을 생성하는 것, 판단하는 것

<div class="comparison">
  <article class="comparison-side">
    <p class="label">GENERATIVE LLM</p>
    <h3>“글을 써주는 AI”</h3>
    <div class="short-flow"><span>State</span><span class="arrow">↓</span><strong>Text</strong></div>
  </article>
  <article class="comparison-side decision">
    <p class="label">JEV / DECISION MODEL</p>
    <h3>“보기 중에서 판단하는 AI”</h3>
    <div class="short-flow"><span>State</span><span class="arrow">↓</span><strong>Decision</strong></div>
  </article>
</div>
<p class="key-message">Unstructured state in.<br><span class="accent">Typed probabilistic decisions out.</span></p>

Note:
**1:10 · Jev in one sentence**
- Jev는 주로 자연어 답변을 쓰는 모델이 아니다. 비정형 state를 받고, 미리 정의된 질문에 typed probabilistic decision으로 답하는 모델이라는 관점이다.
- 입력이 자유롭더라도 출력의 선택 공간은 제한되어 있다. Decision 뒤에는 deterministic code가 이어진다.
- “보기”는 단순 문자열 목록뿐 아니라 boolean, score 등 미리 정의한 판단 공간을 뜻한다.
- 전환: “그런데 지금 Agent에서는 이 작은 판단도 generation으로 처리하는 경우가 많습니다.”

---

<!-- .slide: id="why" data-timing="90" -->

<p class="eyebrow">02 / THE FRICTION</p>

## 작은 판단에 긴 우회로

<div class="problem-layout">
  <div class="questions">
    <p>빠른 모델이면 될까?</p>
    <p>웹 검색이 필요할까?</p>
    <p>승인을 받아야 할까?</p>
    <p>결과가 충분히 좋을까?</p>
    <p>다시 시도해야 할까?</p>
  </div>
  <div class="generation-pipeline" aria-label="기존 generation 기반 판단 흐름">
    <span>Request</span><span class="arrow">↓</span>
    <span>Large LLM</span><span class="arrow">↓</span>
    <span class="mono">“JSON-like” text</span><span class="arrow">↓</span>
    <span>Parse → Validate → Retry?</span><span class="arrow">↓</span>
    <strong>Branch</strong>
  </div>
</div>
<p class="key-message">이미 한정된 판단에 <span class="accent">generation</span>을 쓰고 있다.</p>
<p class="cost-strip">Latency <span>·</span> Tokens <span>·</span> Parsing <span>·</span> Schema failures <span>·</span> Retries</p>

Note:
**1:30 · Why this matters**
- 질문은 “도구를 사용할까?”처럼 bounded인데, 자연어/JSON 생성 후 파싱과 검증을 거쳐야 code가 분기한다.
- Structured output은 형식 안정성을 높일 수 있지만 generation과 typed probabilistic decision은 같은 개념이 아니다.
- Retry?는 일반적인 Agent 패턴이며, 이번 CLI는 자동 retry하지 않는다.
- Latency나 비용은 모델/endpoint에 따라 다르다. 여기서는 수치 우위를 주장하지 않고 구조적인 우회로를 설명한다.
- 전환: “그럼 처음부터 질문과 답의 타입을 정의한다면 어떨까요?”

---

<!-- .slide: id="returns" data-timing="90" -->

<p class="eyebrow">03 / THE CONTRACT <span class="tag">CONCEPT · 측정값 아님</span></p>

## 텍스트 대신, 판단의 계약

<div class="contract-flow">
  <article>
    <p class="label">STATE</p>
    <ul class="plain-list"><li>User request</li><li>Agent state</li><li>Tool state</li><li>Previous results</li></ul>
  </article>
  <span class="arrow">→</span>
  <article class="decision">
    <p class="label">PREDEFINED QUESTIONS</p>
    <ul class="plain-list mono"><li>model_tier?</li><li>needs_web?</li><li>needs_approval?</li></ul>
  </article>
  <span class="arrow accent">→</span>
  <article class="decision">
    <p class="label">TYPED DECISIONS</p>
    <ul class="plain-list"><li><code>FAST</code><small>Choice · 한정된 후보</small></li><li><code>WEB=false</code><small>Boolean · 명시적 타입</small></li><li><code>P(candidate)</code><small>후보별 확률 · 수치 생략</small></li></ul>
  </article>
</div>
<div class="contract-principles"><span>Question is <strong>predefined.</strong></span><span>Answer is <strong>typed.</strong></span><span>Confidence is <strong>explicit.</strong></span></div>
<p class="key-message">Unstructured state → <span class="accent">Decision</span> → Code</p>

Note:
**1:30 · What Jev returns**
- 이 그림은 Decision Model의 개념적 계약이다. 실제 Jev SDK API 문서나 CLI 측정 결과가 아니다.
- 미리 정의된 질문, typed answer, 명시적 확률이 핵심이다. 확률을 threshold로 사용하면 confidence-aware branching도 가능하다.
- Choice/Boolean은 이 발표에서 이해를 돕기 위한 일반 타입 명칭이다. 저장소에 Jev의 Choice/Score/Noul 공식 계약은 정의되어 있지 않아 SDK 타입처럼 주장하지 않는다.
- 현재 CLI의 Ollama fallback은 JSON을 생성·parse하며 candidate probability를 제공하지 않는다. 이 차이는 데모 소개에서 다시 짚는다.
- 전환: “기존 classifier나 LLM JSON과도 겹치는 부분이 있습니다. 목적을 기준으로 비교해 보겠습니다.”

---

<!-- .slide: id="landscape" data-timing="100" -->

<p class="eyebrow">04 / THE LANDSCAPE</p>

## 우열보다, 목적의 차이

<table class="landscape">
  <thead><tr><th>Approach</th><th>주된 역할</th><th>판단의 표현</th></tr></thead>
  <tbody>
    <tr><td>Rule / heuristic</td><td>명시적 조건으로 분기</td><td>조건 → 값</td></tr>
    <tr><td>Traditional classifier</td><td>학습한 label로 분류</td><td>Label / probability</td></tr>
    <tr><td>LLM + structured output</td><td>형식을 제한한 생성</td><td>Generated JSON</td></tr>
    <tr><td>LLM judge</td><td>내용을 평가·비교</td><td>평가 / 점수 생성</td></tr>
    <tr><td>Guard / policy model</td><td>허용 여부를 판정</td><td>Policy verdict</td></tr>
    <tr class="decision-row"><td>Jev / Decision Model</td><td>State의 bounded decision</td><td>Typed / probabilistic</td></tr>
  </tbody>
</table>
<p class="key-message">선택 기준은 <span class="accent">어떤 출력을 필요로 하는가.</span></p>

Note:
**1:40 · Existing approaches**
- 순위표가 아니다. Rules는 명확한 조건에 유리하고 classifier도 typed label과 확률을 제공할 수 있다.
- Structured output은 형식을 제약하고, judge는 평가 역할, guard는 policy 역할에 초점을 둔다. 실제 구현은 서로 겹칠 수 있다.
- Decision Model은 비정형 state에 대한 여러 미리 정의된 질문과 typed/probabilistic 출력을 판단 계층의 중심에 둔다는 framing이다.
- 저장소 원고에 최신 Decisions API 내용이나 공식 계약이 없으므로 특정 외부 API의 기능을 확인 없이 비교하지 않는다.
- 전환: “이 판단 계층을 Agent 전체에 어떻게 배치할까요?”

---

<!-- .slide: id="architecture" data-timing="90" -->

<p class="eyebrow">05 / THE ARCHITECTURE</p>

## System One + System Two

<div class="agent-architecture">
  <div class="agent-head"><strong>Agent</strong><span>지금 필요한 것은 판단인가, 생성인가?</span></div>
  <div class="split-line" aria-hidden="true"><span>↓</span><span>↓</span></div>
  <div class="system-paths">
    <article class="system decision fragment" data-fragment-index="0">
      <p class="label">SYSTEM ONE</p><h3>Jev / Decision Model</h3>
      <p>route · gate · classify</p><p>score · judge · triage</p>
      <small>한정된 판단 공간</small>
    </article>
    <article class="system fragment" data-fragment-index="1">
      <p class="label">SYSTEM TWO</p><h3>Generative LLM</h3>
      <p>reason · write · code</p><p>plan · summarize</p>
      <small>열린 생성 공간</small>
    </article>
  </div>
  <div class="merge-line" aria-hidden="true"><span>↓</span><span>↓</span></div>
  <div class="code-destination mono">Deterministic code</div>
</div>
<p class="key-message">필요한 곳에 생성. <span class="accent">한정된 곳에 판단.</span></p>

Note:
**1:30 · System One + System Two**
- 처음에는 Agent 질문을 보여주고, 첫 fragment에서 bounded decision path, 두 번째에서 generation path를 설명한다.
- System One/Two는 역할을 설명하는 비유다. Jev가 모든 reasoning을 대체한다거나 인간의 인지와 동일하다는 주장이 아니다.
- route/gate/score/filter/triage와 confidence threshold는 판단 계층에, writing/coding/planning/summarization은 생성 계층에 둘 수 있다.
- 두 경로의 결과를 실제로 실행하고 상태를 바꾸는 것은 code다.
- 전환: “이 중 route에 집중한 작은 CLI 데모를 보겠습니다.”

---

<!-- .slide: id="router" data-timing="90" -->

<p class="eyebrow">06 / THE DEMO</p>

## Agent Router: 같은 입력, 같은 schema

<div class="schema-strip mono"><span>model_tier<br><strong>fast / standard / reasoning</strong></span><span>needs_web<br><strong>true / false</strong></span><span>needs_approval<br><strong>true / false</strong></span></div>
<div class="router-architecture">
  <div class="shared-label">SAME FULL REQUEST</div>
  <div class="router-paths">
    <article><span class="arrow">↓</span><h3>LLM Router</h3><p>local LiteLLM</p><code>POST /chat/completions</code><p class="output-label">Generated JSON</p></article>
    <article class="decision"><span class="arrow">↓</span><h3>Jev-like Router</h3><p>local Ollama · generation fallback</p><code>POST /api/generate</code><p class="output-label">Generated JSON</p></article>
  </div>
  <div class="shared-label shared-result">↓<br>Parse / validate → RoutingDecision → CLI 비교</div>
</div>
<p class="footnote">현재 데모는 두 경로 모두 generation. Typed Jev endpoint의 성능 비교는 아닙니다.</p>

Note:
**1:30 · Agent Router**
- 두 Router는 동일한 full request, 동일한 routing policy, 동일한 strict schema를 사용한다. model_tier는 실제로 lowercase다.
- LiteLLM은 OpenAI-compatible /chat/completions, Ollama adapter는 표준 /api/generate에 stream=false, format=json으로 요청한다.
- 개념 슬라이드와 달리 현재 Jev-like adapter도 생성 후 parsing한다. Generation-free, zero tokens, native confidence를 입증하는 데모가 아니다.
- normalized RoutingResult를 Rich UI에서 비교한다. Downstream agent 실행, 웹 검색, DB 변경은 하지 않는다. “Routing result”는 판단 표시다.
- 기본 scenario가 이미 6개 있다. Python Utility → vLLM / CUDA Compatibility → Production DB Cleanup을 사용하면 모델 선택/웹/승인 축을 볼 수 있다.
- 전환: “수치보다 먼저, 어떤 항목을 실제로 관측할 수 있는지 정리하겠습니다.”

---

<!-- .slide: id="measure" data-timing="60" -->

<p class="eyebrow">07 / WHAT TO WATCH</p>

## 숫자는 지금, 터미널에서

<div class="metrics-grid">
  <article><p class="label">LATENCY</p><strong>LIVE</strong><p>응답 + parsing / validation</p></article>
  <article><p class="label">TOKENS</p><strong>LIVE</strong><p>실제 input / output usage</p></article>
  <article class="unavailable"><p class="label">DECISION CONFIDENCE</p><strong>N/A</strong><p>현재 endpoint 미제공</p></article>
  <article><p class="label">SCHEMA / PARSING</p><strong>LIVE</strong><p>성공 여부 · parse time</p></article>
  <article><p class="label">ROUTING RESULT</p><strong>LIVE</strong><p>Tier · Web · Approval</p></article>
</div>
<p class="key-message">같은 판단인가? <span class="accent">어떤 비용으로 얻었는가?</span></p>
<p class="footnote">모델·cold load·출력 차이도 latency에 영향을 줍니다. “—”는 0이 아니라 미관측.</p>

Note:
**1:00 · Demo setup / measurement**
- Latency는 개별 HTTP 호출 직전부터 envelope decoding과 decision parsing/validation 완료까지다. 다른 Router를 기다리는 시간은 포함하지 않는다.
- Token usage는 input/output/total을 각각 실제 API 값으로 표시한다. 빠진 항목만 unavailable이며, 알려진 input/output은 그대로 비교할 수 있다.
- Candidate probabilities는 현재 Ollama 계약에 없어 UI에서 생략된다. 모델이 생성한 확신 표현이나 token logprobs를 confidence로 해석하지 않는다.
- Parse time, failures, errors를 보고 raw output은 o로 확인한다. Cold load, tokenizer, 모델 차이가 있어 방식만의 인과적 benchmark가 아니다.
- 전환: “슬라이드의 LIVE를 실제 관측값으로 바꾸러 터미널로 가겠습니다.”

---

<!-- .slide: id="demo" class="live-demo" data-timing="180" -->

<p class="eyebrow">08 / SWITCH TO TERMINAL</p>

## LIVE DEMO

<p class="demo-statement">Same request.<br>Same decisions.<br><span class="accent">Compare the decision paths.</span></p>

```bash
uv run jev-router-demo
```

<p class="demo-workflow">Scenario <span>→</span> Both routers <span>→</span> Compare</p>
<p class="footnote">실행 위치: repository root · 복귀 후 → Takeaway</p>

Note:
**3:00 · Live demo**
- 터미널로 전환한다. LiteLLM/Ollama와 .env.local을 발표 전에 준비한다. repository root에서 uv run jev-router-demo 실행.
- Python Utility에서 r + Enter: 두 Router를 동시 실행. model_tier, needs_web, needs_approval 비교. 실제 판단은 reference metadata와 다를 수 있다.
- n을 두 번 눌러 vLLM / CUDA Compatibility → r. 외부 최신 정보가 필요하므로 needs_web 판단을 본다.
- n을 두 번 눌러 Production DB Cleanup → r. needs_approval을 본다. 실제 DB 작업은 실행되지 않는다.
- 각 결과에서 latency, input/output tokens, parse 여부를 확인. 시간이 남으면 o로 generated output/raw response 확인 후 Enter로 복귀.
- 연결 실패 시 해당 panel의 실제 오류를 설명하고 다른 backend 결과를 읽는다. 슬라이드에 성공 수치를 만들어 넣지 않는다.
- q로 CLI 종료 → 브라우저 복귀. 현재 #/demo 위치를 유지한다. 오른쪽 화살표 한 번으로 Takeaway.
- 복귀 문장: “같은 schema의 판단을 비교했습니다. 오늘의 takeaway는 특정 숫자가 아니라 생성과 판단의 역할을 분리하는 것입니다.”

---

<!-- .slide: id="takeaway" class="takeaway" data-timing="90" -->

<p class="eyebrow">09 / TAKEAWAY</p>

<h2>Generate when you<br>need generation.</h2>
<h2 class="accent">Decide when you<br>need a decision.</h2>
<p class="complement">Generative LLM <span>+</span> Decision Model</p>
<p class="closing-line">Not everything needs to be a generation.</p>

Note:
**1:30 · Takeaway / Q&A anchor**
- 데모 복귀 후: “이번 구현은 두 경로 모두 generated JSON이었습니다. Native typed/probabilistic decision이 연결된다면 비교할 계약과 관측 기준을 확인한 셈입니다.”
- 생성이 가치 있는 writing, coding, reasoning, planning에는 Generative LLM을 쓴다. 선택 공간이 한정된 route, gate, score에는 Decision Model을 고려한다.
- 둘은 보완 관계다. 판단 뒤 실제 동작은 deterministic code가 담당한다.
- 마지막 문구를 읽고 마무리: Generate when you need generation. Decide when you need a decision.
- Q&A 동안 이 화면을 유지한다. 총 권장 시간 15:00 (CLI demo 3:00 포함).
