# Jev-like Agent Router Demo

15분 발표용 **Textual TUI + 로컬 웹 대시보드**. 같은 요청을 두 backend에
동시에 전송해 **Routing decision layer**의 실제 응답, latency, token usage를
비교합니다. Jev는 System One / Decisions typed API를 지원하며, 로컬 Ollama도
같은 System One adapter를 사용합니다. Downstream agent, web search,
production 작업은 실행하지 않습니다.

## Presentation

Jev와 Decision Model을 소개하는 Slidev 발표(본문 15장 / 15분 + 보충 3장)는
[presentation/README.md](presentation/README.md)를 참고하세요.
개발·정적 빌드·presenter notes·PDF/PPTX 출력·GitHub Pages 배포 및 CLI 데모 전환 방법을 포함합니다.

## Installation

Python 3.12+와 [uv](https://docs.astral.sh/uv/)가 필요합니다.

```bash
uv sync
```

## Configure

```bash
cp .env.example .env.local
```

프로젝트 디렉토리의 `.env.local`에 아래 값을 입력합니다. 기존 환경변수가
우선하며 `.env.local`은 Git에서 제외됩니다.

| 변수 | 설명 |
| --- | --- |
| `LLM_BASE_URL` | OpenAI-compatible LiteLLM base URL, 예: `http://localhost:4000/v1` |
| `LLM_MODEL` | LiteLLM에 등록된 모델 이름 |
| `LLM_API_KEY` | 선택 사항. 비어 있으면 Authorization header를 추가하지 않음 |
| `JEV_API_MODE` | `systemone`(기본) / `decisions`. 기존 `ollama` 값도 `systemone`으로 통합 |
| `JEV_ENDPOINT_URL` | Jev의 완전한 POST URL. 지정하면 경로를 덧붙이지 않음 |
| `JEV_BASE_URL` | 완전한 URL을 지정하지 않을 때 사용. 모드별 `/v1/systemone`, `/alpha/decisions` 경로를 추가 |
| `JEV_API_KEY` | Jev 전용 Bearer key. OpenRouter typed API에서는 필수, 로컬 endpoint에서는 선택 |
| `JEV_MODEL` | 실제 모델 ID, 예: `typesafe/jev-1.13` |
| `REQUEST_TIMEOUT` | 각 HTTP 호출 timeout, 초 단위. 기본 `60` |

시작 시 configuration만 검증하며 endpoint health check는 하지 않습니다.
실제 호출은 Run / `r`에서 시작됩니다. 모델이 없거나 연결이 실패하면 해당 panel에
오류를 표시하고 다른 backend의 결과는 유지합니다.

### Jev: System One / Decisions

Jev는 생성된 문자열을 JSON으로 파싱하는 chat 모델이 아닌 **System One decision
model**입니다. 두 API 경로는 `model + state + questions → answers + usage`라는
typed 계약을 사용합니다.

```dotenv
# TypeSafe / OpenRouter System One
JEV_API_MODE=systemone
JEV_ENDPOINT_URL=https://openrouter.ai/api/v1/systemone
JEV_MODEL=typesafe/jev-1.13
JEV_API_KEY=<your-key>
```

Decisions API를 사용하려면 아래 두 값만 바꿉니다.

```dotenv
JEV_API_MODE=decisions
JEV_ENDPOINT_URL=https://openrouter.ai/api/alpha/decisions
```

로컬 System One 서버도 `JEV_ENDPOINT_URL=http://localhost:8001/v1/systemone`처럼
지정할 수 있습니다. API key는 해당 서버의 인증 요구사항에 따라 설정합니다.
Ollama v0.35.0+와 decision capability가 있는 모델(예: Tev1)을 사용하는 경우:

```dotenv
JEV_API_MODE=systemone
JEV_ENDPOINT_URL=http://localhost:11434/v1/systemone
JEV_MODEL=tev1:4b-q4_K_M
JEV_API_KEY=
```

`JEV_MODEL`에는 로컬에 등록된 실제 모델 이름을 입력합니다. `JEV_API_MODE=ollama`도
동일한 typed API를 선택하며 생성형 `/api/generate` fallback은 제공하지 않습니다.
기존 `JEV_ENDPOINT_URL`이 `/api/generate`로 지정되어 있다면 `/v1/systemone`으로
수정해야 합니다. 설정 변경 후에는 데모를 재시작하세요.

이 데모는 세 질문 모두 `choice`로 요청하여 `fast/standard/reasoning`과
명시적 `true/false` label을 사용합니다. 별도의 숨겨진 Noul 확률 임계값은 없습니다.
반환된 candidate probabilities는 그대로 표시합니다. 예상하지 않은 answer type이나
label은 임의 추정 없이 오류로 표시하고 원본을 보관합니다.

문서: [System One SDK 계약](https://openrouter.ai/docs/guides/community/typesafe-sdk),
[Decisions 튜토리얼](https://openrouter.ai/docs/guides/community/jev-tutorial).

## Run

```bash
# 전체화면 TUI (기본)
uv run jev-router-demo
# 로컬 웹 대시보드
uv run jev-router-demo --web
# 포트 변경
uv run jev-router-demo --web --port 8080
```

웹은 출력된 `http://127.0.0.1:8000` 주소를 브라우저에서 엽니다. 별도 Node 빌드나
CDN이 필요하지 않습니다. 웹도 동일한 Python adapter를 사용하며 브라우저에 API
key를 전달하지 않습니다.

### TUI

명령은 **Enter 없이** 반응하며 버튼 클릭도 가능합니다.

| 명령 | 동작 |
| --- | --- |
| `r` | 현재 요청을 두 backend에 동시에 전송. 각각 완료되는 즉시 결과 표시 |
| `n` / `p` | 현재 분류·검색 결과의 다음 / 이전 시나리오 (순환) |
| `s` | 시나리오 선택 팝업: 추천·전체·유형별 분류와 제목·요약 검색. Enter 선택, Esc 취소 |
| `e` | 여러 줄 request 편집. `Ctrl-S` / Save로 적용, `Esc`로 취소 |
| `c` | 전체 후보·실제 선택·후보 확률과 핵심 측정값을 보여주는 비교 탭 |
| `d` | 선택 상세 탭: 질문별 후보 확률 막대와 `▶` 실제 선택 표시 |
| `x` | 실행 상세 탭: 실제 전송 요청과 전체 측정값 |
| `o` | HTTP inspector 탭 열기 |
| `Tab` / `Shift-Tab` | 조작 영역 사이 focus 이동. focus된 요청 미리보기·JSON 영역에서 방향키 / PageUp / PageDown으로 스크롤 |
| `q` | 종료 |

기본 비교 화면은 **왼쪽 LLM / 오른쪽 JEV**를 명확히 구분하고, 질문별로 전체 후보를
같은 순서와 행에 배치합니다. 후보 옆에 실제 반환된 확률을 표시하고, 실제 선택에는
`●`와 `선택`을 붙입니다. 확률 미제공도 후보를 생략하지 않으며 0%와 구분합니다.
64 columns 이상에서는 좌우 비교를 유지하고, 더 좁으면 질문별 LLM → JEV 순서로
묶어 표시합니다. 상세 측정값과 확률 막대 탭은 100 columns 미만에서 세로 배치합니다.
다른 판단은 `≠`와 색상으로 강조합니다. 선택 상세의 `▶`도 확률이 가장 높은 후보가
아니라 실제 반환된 결정입니다.
요청 원문·전체 측정값, HTTP inspector, 누적 지표는 별도 탭에서 확인합니다.
편집 중에는 `r/n/p/q` 등의 글자를 그대로 입력할 수 있습니다. 실행 중에는 요청 변경과
중복 실행을 비활성화하고 inspector·스크롤은 계속 사용할 수 있습니다.

### 웹

좌측 시나리오 목록 또는 요청 수정으로 입력을 선택한 뒤 비교 실행을 누릅니다.
목록은 추천 6개로 시작하고, 전체 16개와 유형별 분류·제목·요약 검색으로 확장할 수
있습니다. 목록은 독립 스크롤되며 필터 변경은 현재 요청이나 결과를 지우지 않습니다.
800px 이하에서는 목록을 접어 비교 공간을 확보하고, 목록에서 선택하면 다시 접습니다.
`R` / `E` 단축키도 지원합니다. TUI와 동일하게 왼쪽 LLM / 오른쪽 JEV에서 질문별
전체 후보·실제 선택·확률을 같은 순서로 비교합니다. 넓은 화면에서는 확률 막대도
함께 표시하고, 작은 화면에서도 백분율과 선택 표시는 유지합니다. 560px 이하에서는
질문마다 LLM → JEV를 묶어 표시합니다. 확률을 반환하지 않는 LLM도 후보와 선택은
표시하며 확률만 `미제공`으로 구분합니다.
요청 전문·전체 측정값·HTTP 상세·누적 측정값은 접힌 상세 영역에서 확인합니다.

각 TUI 실행과 각 웹 연결은 독립 세션이며 누적 지표를 공유하지 않습니다. 웹 연결이
끊기면 진행 중 호출을 취소하고 Reconnect로 새 세션을 시작합니다. 자동 재실행하지 않습니다.
Expected route는 reference metadata이며 모델의 실제 판단을 덮어쓰지 않습니다.

### 데모 시나리오

총 16개이며 각 요청은 배경·입력 자료·제약조건·최종 요청을 포함한 약 2,800~3,300자의
영문 본문입니다. 제목과 요약은 한국어이며, 화면에서 본문 글자 수와 요청 전문을
확인할 수 있습니다. 긴 입력이 항상 높은 난이도를 뜻하지 않도록 단순 추출·변환도
포함합니다. 기존 6개 시나리오의 순서와 기본 의도는 유지했습니다.

| 분류 | 시나리오 |
| --- | --- |
| 업무·문서 | 회의록 할 일 추출, 고객 안내 메일 초안, 운영 문서 번역 |
| 코딩·디버깅 | Python 리스트 복사, FastAPI 동시성 오류, 로그 JSON 변환 |
| 최신 정보 | vLLM/CUDA 호환성, 최신 API 요금, 최신 보안 공지 |
| 분석·설계 | 저장소 구조, Kubernetes 성능, 제공된 요금표 계산, 출시 계획, DB 삭제 계획 검토 |
| 실행·변경 | 운영 DB 삭제, 운영 배포·권한 변경 |

추천 데모는 Python → FastAPI → 호환성 조회 → 구조 분석 → 운영 DB 삭제 → 회의록
추출의 6개입니다. 전체 목록에서는 최신 API 요금 조회와 제공된 가상 요금표 계산,
운영 DB 삭제와 읽기 전용 삭제 계획 검토를 대비해 볼 수 있습니다.
요금표·로그·업무 기록은 시나리오용 예시이며 실제 시장 가격이나 운영 증거가 아닙니다.
최신 정보가 필요한 요청은 실제 실행 시 모델의 판단을 관찰하는 용도입니다.
시나리오의 기대 경로·추천 여부·분류·한국어 요약은 모델 입력에 추가하지 않습니다.

### HTTP inspector와 긴 JSON

- router별 **Request JSON / Response JSON / Generated / Thinking / HTTP raw text** 탭
- 들여쓰기와 syntax highlighting, 세로·가로 스크롤
- 480자 초과 문자열 값은 **앞 320자 + `… [중략: N자] …` + 뒤 120자**로 표시
- JSON 구조와 숫자·boolean은 유지. 기본 화면에 `요약 표시 · 원본 변경 없음` 안내
- **Show full**로 전체 보기. 실제 모델에 전송하는 바디와 보관 원본은 중략하지 않음
- **TUI Export original**: 작업 디렉토리의 Git 제외 `exports/`에 새 이름으로 저장
- **웹 Copy original / Save original**: 요약이 아닌 원본을 클립보드 / 다운로드로 제공
- HTTP 오류·비 JSON 응답도 바디 보관. 너무 깊게 중첩된 JSON은 원문 텍스트로 확인
- System One/Decisions는 generated text와 thinking이 없으므로 해당 탭에 미제공 안내

전체 응답의 정확한 디코딩 텍스트는 HTTP raw text 탭에서 확인합니다. JSON 탭은
해독된 JSON에 들여쓰기를 적용한 보기입니다. 네트워크 패킷의 byte-level dump는 아닙니다.

### 기존 CLI 자동화

```bash
uv run jev-router-demo --cli
# 파이프 입력은 기존 line-oriented CLI로 자동 전환
printf 'n\np\nq\n' | uv run jev-router-demo
```

기존 CLI에서는 명령 뒤에 Enter를 누릅니다. `v`로 요청 전문, `o`로 generated output·
thinking·API response를 볼 수 있습니다. `uv run python -m jev_router_demo`도 같은 옵션을 지원합니다.

## Architecture

```text
same full request
  ├── LiteLLM generative router · POST /chat/completions
  └── Jev System One / Decisions adapter
        └── OpenRouter / local Ollama · state + typed questions
             ↓
      normalized RoutingResult
             ↓
   incremental session + in-memory metrics + original HTTP exchange
             ├── Textual TUI
             └── FastAPI WebSocket + local web dashboard
```

### Jev-like compatibility

**System One/Decisions adapter**는 `Decision output = typed`, generated-decision
parse는 `Not required`로 표시합니다. HTTP envelope decoding과 typed answer validation은
latency에 포함합니다. `usage.output_tokens`가 반환되면 0으로 덮어쓰지 않으며,
generated text/bytes가 미제공이면 unavailable로 표시합니다.

로컬 Ollama도 같은 typed 계약을 사용합니다. 없는 API나 가짜 zero-token/confidence
값은 사용하지 않습니다. LiteLLM 경로만 generated decision JSON을 생성·parse합니다.

Typed 계약은 `src/jev_router_demo/routers/systemone.py`에 통합돼 있습니다.
실제 API가 제공하는 candidate probabilities만 표시하며 미제공이면 section을 생략합니다.
Token logprobs를 candidate probability로 간주하지 않습니다.

### Measurement interpretation

- Latency: 각 HTTP 호출 직전부터 응답 decoding과 decision parsing/validation
  완료까지의 wall-clock 시간. 다른 router의 완료를 기다리는 시간은 포함하지 않음.
- Parse time: generated decision JSON의 fence 처리·parsing·validation 시간.
  HTTP envelope decoding은 latency에만 포함됩니다.
- Token usage: LiteLLM `usage`의 실제 값. 로컬 Ollama를 포함한 System One/Decisions는
  `usage.input_tokens` / `usage.output_tokens`입니다.
  Typed API의 total은 제공된 input + output count의 합입니다.
- Generated bytes: 반환된 routing text와 별도 thinking/reasoning text의 UTF-8 byte
  합계입니다. HTTP envelope 크기나 반환되지 않은 내부 generation 크기가 아닙니다.
- 평균 latency는 성공한 요청만 포함합니다. Requests / errors에는 실패도 포함됩니다.
  Parse failures는 decision parsing을 시도한 뒤 실패한 경우만 셉니다.
- 누적 usage에는 실패 응답에서도 얻은 실제 usage가 포함됩니다. 일부 요청에서만
  관측된 합계는 `(관측 건수/전체 요청 수)`를 붙입니다. `-`는 unavailable이며 0과 다릅니다.
- Cold model load, prompt templating, cache, tokenizer, 출력 형식 및 모델 차이도
  측정에 영향을 줍니다. 이 화면은 관측값이며 router 방식만의 인과적 성능 비교는 아닙니다.

## Tests

```bash
uv run pytest
```

Parsing, metrics, dotenv, HTTP 계약·오류 격리·동시 실행, UI와 CLI 입력을
검증합니다. System One/Decisions 계약, HTTP 원본 보존·중략·취소·부분 결과,
Textual Pilot 동작과 웹 WebSocket 세션도 포함합니다. 기본 테스트에는 실제 endpoint가 필요하지 않습니다.
실제 decision 품질 및 latency 비교는 설정한 실제 endpoint에 호출한 뒤 확인합니다.

시각적 smoke 검증용 synthetic fixture도 제공합니다. fixture의 응답·수치는 실제
모델의 decision 품질이나 성능을 나타내지 않습니다.

```bash
uv run python tests/browser_demo_server.py  # http://127.0.0.1:8765
uv run python tests/capture_tui.py          # exports/tui-*.svg
```

브라우저 탐색 회귀 검증은 fixture 서버 실행 후 Playwright MCP의
`browser_run_code`에 `tests/browser_scenarios_smoke.js` 내용을 전달하거나, 허용된
프로젝트 경로에서 `filename`으로 실행할 수 있습니다. 분류·검색 후 실제 선택 표시,
요청 전문 보존, 빈 결과, 모바일 목록 접힘을 확인합니다.

브라우저 fixture에서 직접 입력 요청에 `__comparison_edges__`를 넣으면 실제 선택과
최대 확률 후보가 다른 경우, 일부 후보의 확률 미제공, 선택된 후보의 0%를 확인할 수
있습니다. `__http_error__`는 LLM 호출 실패와 JEV 부분 결과를 확인하는 fixture입니다.
