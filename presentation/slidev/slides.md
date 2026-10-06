---
theme: default
title: Jev — 생성과 판단을 나누는 Agent 설계
info: |
  개발자·AI 엔지니어 대상 · 본문 15장 / 15분 + 보충 3장.
  Agent Router CLI는 별도 터미널에서 실행합니다.
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
layout: default
class: opening
---

<div class="eyebrow">JEV / DECISION MODELS FOR AGENTS</div>

# 작은 판단에도<br>큰 생성이 필요할까?

<div class="opening-subtitle">생성과 판단을 나누는 Agent 설계</div>
<div class="opening-bottom"><span class="brand">Jev</span><span class="muted">문제 → 판단 계약 → Agent Router → 데모</span></div>

<!--
0:30 · Opening
- 개발자·AI 엔지니어 대상. Agent가 답을 쓰기 전 수행하는 작은 판단에 집중한다.
- 오늘의 질문: 모델 선택, 검색, 승인도 모두 긴 답변 생성으로 풀어야 할까?
- Jev는 이 발표에서 Decision Model의 관점으로 설명한다. 특정 SDK의 검증된 기능 목록은 아니다.
- 전환: “실제 요청 하나부터 보겠습니다.”
-->

---
layout: default
---

<div class="eyebrow">문제 / AGENT의 작은 선택</div>

## 답을 쓰기 전에, 먼저 골라야 한다

<div class="request-block"><span class="label">USER REQUEST · PYTHON UTILITY 요약</span><p>“원본을 바꾸지 않고 리스트를 뒤집는<br>간단한 Python 코드와 동작을 설명해줘.”</p></div>
<div class="three-columns decision-questions">
  <article><span class="step">01</span><h3>어떤 모델?</h3><p>fast / standard / reasoning</p></article>
  <article><span class="step">02</span><h3>웹 검색이 필요할까?</h3><p>true / false</p></article>
  <article><span class="step">03</span><h3>승인이 필요할까?</h3><p>true / false</p></article>
</div>
<div class="key-message">결과물은 코드·설명이지만, 앞단의 질문은 <span class="accent">한정된 선택</span>이다.</div>

<!--
0:50 · Concrete request
- 요청 문장은 설명용 축약이다. 데모에서는 저장소의 Python Utility 입력 전문을 그대로 사용한다.
- 코드와 설명을 작성하는 작업은 generation, 그 전에 모델/웹/승인을 고르는 작업은 bounded decision이다.
- 어떤 답이 나올지는 정책과 모델에 따라 달라진다. 여기서 정답을 고정하지 않는다.
- 전환: “이 선택을 지금은 어떤 경로로 얻고 있을까요?”
-->

---
layout: default
---

<div class="eyebrow">문제 / GENERATION 기반 판단</div>

## 필요한 것은 값인데, 먼저 텍스트를 만든다

<div class="pipeline">
  <article><span class="label">INPUT</span><h3>요청 + 정책</h3></article><span class="arrow">→</span>
  <article><span class="label">GENERATE</span><h3>LLM</h3><p>JSON 텍스트 생성</p></article><span class="arrow">→</span>
  <article><span class="label">CHECK</span><h3>Parse / Validate</h3><p>실패하면 재시도?</p></article><span class="arrow">→</span>
  <article class="decision"><span class="label">USE</span><h3>코드 분기</h3></article>
</div>
<div class="code-example"><span class="label">GENERATED TEXT → VALIDATED VALUE</span><code>{ "model_tier": "fast", "needs_web": false, "needs_approval": false }</code></div>
<div class="key-message">판단의 비용에는 <span class="accent">생성·검증 경로</span>도 포함된다.</div>
<div class="footnote">Latency · Tokens · Schema failures · Retries — 효과의 크기는 실제 환경에서 확인</div>

<!--
1:00 · Current path
- 이미 후보가 정해진 질문인데도 텍스트 생성 후 파싱·검증으로 code가 사용할 값을 얻는다.
- Structured output은 형식 안정성을 높일 수 있다. 모든 LLM 경로가 느리거나 실패한다는 주장은 아니다.
- JSON은 설명용 예시, 실측 출력이 아니다. Retry?는 일반 패턴이고 현재 CLI는 자동 retry하지 않는다.
- 전환: “핵심은 LLM의 크기보다, 필요한 출력의 성격입니다.”
-->

---
layout: default
---

<div class="eyebrow">관점 / 출력 공간을 기준으로</div>

## 열린 답을 만드는 일과, 선택하는 일

<div class="comparison">
  <article class="compare-side" v-click="1"><span class="label">GENERATE</span><h3>무엇을 만들어낼까?</h3><p>코드 · 설명 · 계획 · 요약</p><div class="big-word">열린 출력</div><span class="muted">State → Text / Code</span></article>
  <article class="compare-side decision" v-click="2"><span class="label">DECIDE</span><h3>어느 쪽을 선택할까?</h3><p>모델 · 검색 · 승인 · 재시도</p><div class="big-word accent">정해진 판단 공간</div><span class="muted">State → Typed decision</span></article>
</div>
<div class="key-message" v-click="3">같은 Agent 안에서도 <span class="accent">다른 출력 계약</span>이 필요하다.</div>

<!--
0:50 · Generate vs decide
- Click 1: 열린 답을 작성. Click 2: 정해진 판단 공간. Click 3: 역할을 분리할 수 있다는 핵심.
- “보기”는 enum만이 아니라 boolean, 정해진 범위의 score 같은 출력도 포함한다.
- LLM도 판단에 쓸 수 있다. 이 구분은 능력의 독점이 아니라 역할과 계약에 관한 것이다.
- 전환: “Jev를 이 판단 계층의 관점에서 소개하겠습니다.”
-->

---
layout: default
class: statement-slide
---

<div class="eyebrow">관점 / JEV · DECISION MODEL</div>

## 입력은 자유롭게.<br><span class="accent">판단은 정해진 계약으로.</span>

<div class="definition">비정형 상태를 받아,<br>미리 정의된 질문에 <strong>typed / probabilistic decision</strong>으로 답하는 판단 계층.</div>
<div class="definition-principles"><span>State</span><span class="arrow">→</span><span class="accent">Decision</span><span class="arrow">→</span><span>Code</span></div>
<div class="footnote">여기서는 개념적 역할을 설명합니다. 공식 SDK/API 계약이나 성능 수치를 가정하지 않습니다.</div>

<!--
0:50 · Definition
- Unstructured state in, typed probabilistic decisions out이라는 관점.
- 비정형 request/context를 받아도 질문과 답의 공간을 미리 정의한다.
- 확률을 제공하는 계약이라면 그 값을 후속 분기에 사용할 수 있다. 실제 지원 여부는 endpoint 계약 확인이 필요하다.
- Jev 모델의 내부 구조나 모든 reasoning의 대체를 주장하지 않는다.
- 전환: “앞의 Python 리스트 요청을 이 계약에 넣어보겠습니다.”
-->

---
layout: default
---

<div class="eyebrow">계약 / CONCEPT <span class="tag">설명용 예시 · 실측 아님</span></div>

## 질문과 답의 타입을 먼저 정의한다

<div class="contract-flow">
  <div class="state-column"><span class="label">UNSTRUCTURED STATE</span><h3>Python 리스트 요청</h3><p>사용자 요청<br>Agent context<br>Tool state<br>이전 결과</p></div>
  <span class="arrow accent">→</span>
  <div class="decision-stack">
    <DecisionCard label="model_tier?" value="fast" detail="Choice · fast / standard / reasoning" />
    <DecisionCard label="needs_web?" value="false" detail="Boolean · true / false" />
    <DecisionCard label="needs_approval?" value="false" detail="Boolean · true / false" />
  </div>
</div>
<div class="key-message">질문은 미리 정의하고, <span class="accent">답은 코드가 사용할 타입으로.</span></div>

<!--
1:00 · Typed contract
- 같은 사례를 유지한다. 오른쪽 값은 설명용이며 실제 router가 이 값을 내야 한다는 뜻이 아니다.
- question별 출력 공간과 schema를 미리 결정한다. Choice/Boolean은 일반 타입 명칭이지 공식 Jev SDK 타입이 아니다.
- 현재 CLI에도 typed RoutingDecision이 있지만 JSON을 생성·파싱한 뒤 얻는다. Native decision output과 구분한다.
- 전환: “확률이 제공된다면, 선택한 값 외에도 분기 근거를 얻을 수 있습니다.”
-->

---
layout: default
---

<div class="eyebrow">계약 / PROBABILITY → POLICY <span class="tag">개념적 흐름</span></div>

## 확률을 제공한다면, 분기는 코드가 맡는다

<div class="policy-flow">
  <article><span class="label">MODEL OUTPUT</span><h3>후보별 확률</h3><div class="probability-list mono">P(fast)<br>P(standard)<br>P(reasoning)</div><p class="muted">endpoint가 제공하는 값</p></article>
  <span class="arrow accent">→</span>
  <article class="decision"><span class="label">APPLICATION POLICY</span><h3>검증한 기준과 비교</h3><p>선택한 후보의 확률<br>업무 위험도 · 적용 정책</p><span class="muted">threshold는 앱이 결정</span></article>
  <span class="arrow">→</span>
  <article><span class="label">CODE BRANCH</span><h3>실행 또는 보류</h3><p>선택한 경로 사용<br>더 강한 모델로 전환<br>추가 판단 요청</p></article>
</div>
<div class="key-message">확률은 입력 신호다. <span class="accent">실행 정책은 모델 밖에 둔다.</span></div>
<div class="footnote">확률 ≠ 정확성 보장. Calibration·threshold 검증이 필요하며 현재 CLI는 후보 확률을 제공하지 않습니다.</div>

<!--
0:50 · Probability to policy
- 수치를 만들어 보여주지 않는다. 후보별 probability가 제공될 때 가능한 개념적 branching이다.
- calibration 없이 높은 확률을 정확성 보장으로 읽으면 안 된다. threshold는 validation set과 위험도에 맞춰 검증한다.
- 모델이 생성한 “확신합니다”나 token logprobs를 candidate probability로 대신하지 않는다.
- 전환: “Agent 안에서는 이 판단 계층과 생성 계층이 어떻게 연결될까요?”
-->

---
layout: default
---

<div class="eyebrow">설계 / COMPLEMENTARY LAYERS</div>

## 판단으로 경로를 고르고, 생성으로 작업한다

<div class="agent-chain">
  <article><span class="label">STATE</span><h3>요청 + 맥락</h3></article><span class="arrow">→</span>
  <article class="decision" v-click="1"><span class="label">DECIDE</span><h3>판단 계층</h3><p>route · gate · triage</p></article><span class="arrow" v-click="1">→</span>
  <article v-click="2"><span class="label">GENERATE / TOOLS</span><h3>선택한 경로</h3><p>write · code · search</p></article>
</div>
<div class="execution-bar" v-click="3"><span class="label">DETERMINISTIC CODE</span><span>Schema 검증 → 정책 적용 → 호출·실행 → 상태 갱신</span></div>
<div class="key-message" v-click="3">Decision Model은 생성 모델의 <span class="accent">대체가 아니라 보완</span>이다.</div>
<div class="footnote">역할을 나눈 개념도입니다. 요청에 따라 모델 호출을 생략하거나 판단을 반복할 수 있습니다.</div>

<!--
1:00 · Agent architecture
- Click 1: bounded decision 계층. Click 2: 선택된 생성·도구 경로. Click 3: 실제 호출/실행은 code가 담당.
- System One/Two 비유 대신 명시적인 데이터 흐름을 사용한다. 불필요한 인지과학 해석을 피한다.
- Rules로 바로 결정할 수 있는 경우는 모델 호출을 생략할 수 있다. 이후 결과가 state로 돌아가 다시 판단될 수 있다.
- 그림은 목표 아키텍처다. 현재 CLI는 선택한 downstream 경로를 실행하지 않는다.
- 전환: “그렇다면 언제 어떤 판단 방식을 쓰는 게 좋을까요?”
-->

---
layout: default
---

<div class="eyebrow">설계 / 도구 선택 기준</div>

## 필요한 계약에 맞춰 판단 방식을 고른다

<div class="selection-grid">
  <article><span class="label">명시적인 조건</span><h3>Rule / heuristic</h3><p>조건이 분명하고 코드로 유지할 수 있다.</p></article>
  <article><span class="label">고정된 분류 과제</span><h3>Classifier</h3><p>학습 데이터와 label 공간이 준비되어 있다.</p></article>
  <article><span class="label">생성과 평가를 함께</span><h3>LLM + structured output</h3><p>유연한 추론·설명과 정해진 형식이 필요하다.</p></article>
  <article class="decision"><span class="label">비정형 상태의 반복 판단</span><h3>Decision Model</h3><p>미리 정의된 질문과 typed / probabilistic 계약이 중심이다.</p></article>
</div>
<div class="key-message">새 모델부터 고르기보다, <span class="accent">질문·출력·검증 기준부터.</span></div>

<!--
0:50 · Selection criteria
- 우열표가 아니라 선택의 출발점이다. Classifier도 typed label/probability를 제공하며 접근 간 기능은 겹친다.
- LLM judge와 guard/policy는 평가·정책 역할을 가리킨다. 구현은 rule/classifier/LLM 등에 걸칠 수 있다.
- Decision Model을 늘 최선으로 결론내리지 않는다. latency, 품질, 운영 복잡도는 검증해야 한다.
- 상세 비교는 보충 A. 전환: “이제 지금 구현된 범위와 목표 계약을 분리해서 데모를 보겠습니다.”
-->

---
layout: default
---

<div class="eyebrow">데모 / CONCEPT ≠ CURRENT IMPLEMENTATION</div>

## 오늘 확인하는 것은 Router 비교의 기반이다

<div class="comparison scope-comparison">
  <article class="compare-side decision"><span class="label">개념적 목표</span><h3>Typed / probabilistic 판단</h3><ul><li>정해진 질문과 타입</li><li>후보별 확률이 있는 출력 계약</li><li>정책에 따른 코드 분기</li></ul></article>
  <article class="compare-side"><span class="label">현재 CLI 구현</span><h3>두 backend의 JSON 생성</h3><ul><li>LiteLLM / Ollama 호출</li><li>JSON parse / schema validation</li><li>판단·비용 표시, 후보 확률 미제공</li></ul></article>
</div>
<div class="callout">이 데모는 native typed Jev endpoint의 성능 우위를 입증하지 않습니다.</div>
<div class="footnote">입력·schema·관측 기준을 맞춘 비교 harness입니다. 웹 검색·DB 변경은 실행하지 않습니다.</div>

<!--
0:50 · Demo scope
- 개념에서 실제 구현으로 넘어가는 명시적인 경계다. Jev-like 이름 때문에 native Jev API로 오해하지 않도록 설명한다.
- 현재 Ollama adapter도 generation fallback이다. Native confidence, generation-free, zero tokens를 입증하지 않는다.
- 이 데모의 가치는 동일한 판단 문제를 두 backend에 보내고 결과와 비용을 나란히 관측하는 구조다.
- 전환: “무엇을 동일하게 맞췄는지 보겠습니다.”
-->

---
layout: default
---

<div class="eyebrow">데모 / COMPARISON HARNESS</div>

## 같은 요청·정책·schema, 다른 backend

<div class="shared-request">SAME FULL REQUEST + ROUTING POLICY</div>
<div class="router-paths">
  <article><span class="label">LLM ROUTER</span><h3>LiteLLM</h3><code>POST /chat/completions</code><p>Generated JSON</p></article>
  <article><span class="label">JEV-LIKE ROUTER · FALLBACK</span><h3>Ollama</h3><code>POST /api/generate</code><p>Generated JSON</p></article>
</div>
<div class="shared-result">↓ Parse / Validate → <strong class="accent">RoutingDecision</strong> → CLI 비교</div>
<div class="schema-strip mono"><div>model_tier<strong>fast / standard / reasoning</strong></div><div>needs_web<strong>true / false</strong></div><div>needs_approval<strong>true / false</strong></div></div>
<div class="footnote">두 호출은 동시에 실행합니다. Backend·모델 차이도 결과에 영향을 줍니다.</div>

<!--
0:50 · Harness
- 두 Router는 동일한 full request, routing policy, strict schema를 사용한다. model_tier 실제 값은 lowercase다.
- LiteLLM은 OpenAI-compatible chat completions, Ollama는 /api/generate에 stream=false, format=json.
- UI는 normalized RoutingResult를 비교하고 실제 후속 실행은 하지 않는다.
- 동일 schema가 품질·속도의 동일성을 뜻하지는 않는다. 모델 차이도 함께 존재한다.
- 전환: “세 장면에서 판단의 세 축을 관찰하겠습니다.”
-->

---
layout: default
---

<div class="eyebrow">데모 / 먼저 판단, 그다음 비용</div>

## 세 장면에서 모델·검색·승인을 본다

<div class="three-columns scenario-grid">
  <article><span class="step">01 / MODEL</span><h3>Python Utility</h3><p>작은 코드·설명 요청</p><div class="scenario-question">어떤 tier를 고를까?</div></article>
  <article><span class="step">02 / WEB</span><h3>vLLM / CUDA</h3><p>호환성 정보 확인</p><div class="scenario-question">최신 정보가 필요할까?</div></article>
  <article><span class="step">03 / APPROVAL</span><h3>Production DB</h3><p>운영 데이터 정리 요청</p><div class="scenario-question">승인 없이 진행할까?</div></article>
</div>
<div class="watch-strip"><strong>판단 결과</strong><span>→</span><span>Latency</span><span>·</span><span>Input / output tokens</span><span>·</span><span>Parsing</span></div>
<div class="footnote">예상 경로는 scenario metadata입니다. 실제 모델의 응답을 덮어쓰지 않습니다. Confidence는 현재 미제공.</div>

<!--
0:40 · Demo cues
- 저장소의 Python Utility, vLLM / CUDA Compatibility, Production DB Cleanup 순으로 본다.
- route를 먼저 읽고 latency/tokens/parse를 본다. 모델이 reference와 다르면 어떤 정책을 해석했는지 raw output을 확인한다.
- v는 입력 전문, o는 raw/generated output. Expected route는 model 평가의 정답으로 자동 사용하지 않는다.
- 실제 웹 검색이나 DB 작업은 일어나지 않는다. 전환: “터미널로 가겠습니다.”
-->

---
layout: default
class: live-demo
---

<div class="eyebrow">데모 / SWITCH TO TERMINAL</div>

# 같은 질문을 보내고,<br><span class="accent">실제 판단을 비교한다.</span>

```bash
uv run jev-router-demo
```

<div class="demo-workflow"><span><kbd>r</kbd> 두 Router 실행</span><span><kbd>n</kbd> 다음 scenario</span><span><kbd>o</kbd> 응답 확인</span><span><kbd>q</kbd> 종료</span></div>
<div class="footnote">Repository root에서 실행 · 각 명령 뒤 Enter · 복귀 후 → 결과 해석</div>

<!--
3:00 · Live demo
- 사전 준비: .env.local, LiteLLM/Ollama 모델, 넓은 터미널. 실행 위치는 repository root.
- Python Utility에서 r + Enter → Tier/Web/Approval → latency/tokens/parse 비교.
- n 두 번 → vLLM / CUDA Compatibility → r: needs_web. n 두 번 → Production DB Cleanup → r: needs_approval.
- 여유 있으면 o → generated/raw output → Enter. v는 입력 전문. 실제 판단과 오류를 있는 그대로 읽는다.
- 연결 실패 시 실제 오류와 다른 panel 결과를 설명한다. 숫자를 지어내거나 준비된 성공값으로 대체하지 않는다.
- q → 브라우저 /13 또는 #/13 복귀 → 오른쪽 화살표 한 번으로 결과 해석 /14.
- 복귀 문장: “판단 결과와 그 결과를 얻는 비용을 봤습니다. 무엇까지 결론낼 수 있을까요?”
-->

---
layout: default
---

<div class="eyebrow">해석 / OBSERVATION → NEXT VALIDATION</div>

## 판단 품질과 실행 비용을 함께 읽는다

<div class="comparison interpretation">
  <article class="compare-side"><span class="label">지금 관측한 것</span><h3>이번 호출의 결과</h3><ul><li>Tier / Web / Approval의 일치·차이</li><li>응답 + 검증까지의 latency</li><li>API usage와 parse 성공·실패</li></ul></article>
  <article class="compare-side decision"><span class="label">다음에 검증할 것</span><h3>실제 적용 가능성</h3><ul><li>평가셋에서의 판단 품질·일관성</li><li>반복 측정, cold / warm 조건</li><li>Native 계약 연결 후 확률·정책 검증</li></ul></article>
</div>
<div class="key-message">한 번의 빠른 응답이 <span class="accent">더 나은 판단 계층</span>을 뜻하지는 않는다.</div>
<div class="footnote">모델·tokenizer·cold load가 함께 달라집니다. “—”는 0이 아니라 미관측이며, 이번 호출만으로 방식의 우위를 결론내리지 않습니다.</div>

<!--
1:00 · Interpret live observations
- 방금 관측한 실제 결과를 먼저 말한다. 승자를 미리 지정하거나 정적인 성공 수치를 추가하지 않는다.
- 일치했다고 모두 정확한 것은 아니다. 차이가 나면 request와 policy에 근거해 해석한다.
- Latency는 개별 HTTP 호출 직전부터 decoding 및 parsing/validation 완료까지, 상대 Router 대기 제외.
- 높은 확률의 타당성은 calibration 평가가 필요하다. 현재 confidence는 미제공.
- 전환: “마지막으로 Agent를 설계할 때의 기준을 정리하겠습니다.”
-->

---
layout: default
class: takeaway
---

<div class="eyebrow">TAKEAWAY / Q&A</div>

<div class="takeaway-line">생성이 필요한 곳에는 생성.</div>
<div class="takeaway-line accent">한정된 선택에는 판단.</div>
<div class="takeaway-actions"><span>질문을 정의한다</span><span>→</span><span>출력 계약을 고른다</span><span>→</span><span>품질과 비용을 검증한다</span></div>
<div class="closing-line">Generative LLM <span class="accent">+</span> Decision Model</div>
<div class="footnote">Not everything needs to be a generation.</div>

<!--
1:00 · Takeaway / Q&A
- Generative LLM과 Decision Model은 보완 관계다. 어떤 모델이냐 전에 필요한 질문과 출력 계약을 정의한다.
- 열린 writing/coding/planning에는 생성, 한정된 route/gate/triage에는 판단 계층을 고려한다.
- 실제 실행은 code, 적용 여부는 품질과 비용으로 검증한다. 지금 CLI는 그 비교 기반이며 native typed endpoint는 아니다.
- Q&A는 이 화면 유지. 본문 15장 notes 합계 15:00, demo/전환 3:00 포함. 이후 3장은 보충 자료.
-->

---
layout: default
class: appendix
---

<div class="eyebrow">보충 A / APPROACHES</div>

## 구현 방식과 역할은 겹칠 수 있다

| Approach | 주된 역할 | 판단의 표현 |
| --- | --- | --- |
| Rule / heuristic | 명시적 조건으로 분기 | 조건 → 값 |
| Traditional classifier | 학습한 label로 분류 | Label / probability |
| LLM + structured output | 형식을 제한한 생성 | Generated JSON |
| LLM judge | 내용을 평가·비교 | 평가 / 점수 |
| Guard / policy model | 허용 여부 판정 | Policy verdict |
| Jev / Decision Model | 비정형 state의 bounded decision | Typed / probabilistic 계약 |

<div class="footnote">우열표나 상호 배타적인 분류가 아닙니다. Judge·guard는 역할이며 여러 구현 방식을 사용할 수 있습니다.</div>

<!--
보충 · 본문 시간에서 제외
- classifier도 typed label과 probability를 제공한다. Decision Model만 가능한 출력이라고 주장하지 않는다.
- 정량 비교는 동일 평가셋, 조건, 실제 endpoint 계약을 갖춘 뒤 수행한다.
-->

---
layout: default
class: appendix
---

<div class="eyebrow">보충 B / MEASUREMENT DEFINITIONS</div>

## 비교 화면의 숫자는 무엇을 포함할까?

<div class="metrics-grid">
  <MetricCard label="LATENCY" value="wall-clock" detail="개별 HTTP 요청 시작 → decoding + 판단 검증 완료. 다른 Router의 대기 시간 제외." />
  <MetricCard label="TOKENS" value="API usage" detail="실제 input / output 사용량. 모델별 tokenizer 차이와 미관측 항목을 구분." />
  <MetricCard label="PARSING" value="parse + validate" detail="판단 JSON 처리·검증 시간. HTTP envelope decoding은 latency에만 포함." />
  <MetricCard label="CANDIDATE PROBABILITY" value="N/A" detail="현재 endpoint 미제공. 생성한 확신 표현·token logprobs로 대체하지 않음." />
</div>
<div class="footnote">Cold load·cache·모델·출력 길이도 영향을 줍니다. 현재 CLI의 자세한 집계 기준은 repository README를 참고하세요.</div>

<!--
보충 · 본문 시간에서 제외
- Ollama input=prompt_eval_count, output=eval_count, 둘 다 있으면 total 합산. LiteLLM은 usage.
- Generated bytes는 반환된 routing text + 별도 thinking text의 UTF-8 bytes, HTTP envelope가 아니다.
- 성공 요청만 평균 latency에 포함, errors에는 실패 포함. 실제 usage는 실패 응답에서도 유지.
-->

---
layout: default
class: appendix
---

<div class="eyebrow">보충 C / FROM HARNESS TO NATIVE CONTRACT</div>

## Native 판단 endpoint를 연결할 때

<div class="three-columns integration-grid">
  <article><span class="step">01 / CONTRACT</span><h3>실제 응답 계약 확인</h3><p>질문·출력 타입<br>후보 확률의 의미<br>실패·미제공 표현</p></article>
  <article><span class="step">02 / ADAPTER</span><h3>전송·정규화 연결</h3><p>실제 API로 요청<br>RoutingResult로 변환<br>제공된 metric만 기록</p></article>
  <article><span class="step">03 / EVALUATION</span><h3>품질·정책 검증</h3><p>공통 평가셋<br>반복·조건별 측정<br>Calibration·threshold</p></article>
</div>
<div class="callout mono">src/jev_router_demo/routers/ollama_jev.py</div>
<div class="footnote">현재 연결 지점: build_jev_prompt() · parse_jev_response() · OllamaJevRouter.route(). 없는 API나 가짜 metric을 추가하지 않습니다.</div>

<!--
보충 · 본문 시간에서 제외
- 실제 API 확인이 먼저다. typed output이면 output_kind=typed, parse_required=False로 normalize하고 실제 제공 metric만 채운다.
- Candidate probabilities 계약이 확인되면 RoutingResult.probabilities 사용. 이름만 바꿔 JSON generation을 native output처럼 취급하지 않는다.
- Q&A 마무리는 /15로 복귀.
-->
