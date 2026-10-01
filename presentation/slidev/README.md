# Jev Slidev Presentation

기존 [`../talk.md`](../talk.md)를 시각적으로 압축한 **10장, 약 15분** 발표입니다.
Reveal.js와 독립적으로 실행합니다. CLI live demo는 실제 terminal에서 진행합니다.

## Requirements

- **Node.js >=22.12.0**, npm. 설치한 `@slidev/cli@53.0.0`의 engines 기준입니다.
- Node.js **24 LTS**로 install/build/export를 검증했습니다. 의존성
  `postcss-nested@8`은 Node 22/24 또는 26 이상을 지원하므로 LTS를 사용하세요.
- 한국어가 표시되는 OS system font가 필요합니다. Google Fonts나 원격 font를
  사용하지 않습니다. Code는 OS monospace fallback을 사용합니다.

## Install

Repository root에서:

```bash
cd presentation/slidev
npm install
```

Lockfile로 동일한 의존성을 설치할 때는 `npm ci`를 사용합니다. 설치·browser
다운로드는 인터넷이 필요하지만 이후 dev/build/발표/export에는 필요하지 않습니다.
Slidev의 Twoslash tooltip과 `floating-vue@5.4`의 호환 오류를 피하기 위해
`floating-vue@5.2.2`를 override로 고정했습니다.

## Development

```bash
npm run dev
```

기본 audience URL: **http://localhost:3030/1**. 브라우저를 자동으로 엽니다.
포트를 명시하려면 `npm run dev -- --port 3030`. 서버는 기본 loopback입니다.
Monaco, slide 내부 실행, remote API, iframe은 사용하지 않습니다.

## Build

```bash
npm run build
npm run preview
```

`dist/`는 정적 web application입니다. Preview 기본 주소는
**http://127.0.0.1:4173/#/1**. `file://` 대신 local HTTP server를 사용하세요.
Build는 hash routing을 사용해 static hosting에서도 slide URL 새로고침이 가능합니다.
포트가 사용 중이면 다른 포트를 선택하므로 실행 시 표시된 URL을 확인하세요.

### GitHub Pages / sub-path

```bash
npm run build -- --base /jev-router-demo/slidev/
npm run preview -- --base /jev-router-demo/slidev/
```

Sub-path preview: **http://127.0.0.1:4173/jev-router-demo/slidev/#/1**.
배포 시 `dist/` 내부 전체를 해당 사이트의 `slidev/` 경로에 배치합니다.
Base는 `/`로 시작하고 끝나야 합니다. Reveal 결과물과 별도 경로로 배포하면
둘이 공존합니다. 이 작업은 Pages deployment workflow를 추가하지 않습니다.
발표만 단독으로 repo 경로에 배포하려면 실제 배포 위치에 맞는 base를 전달하세요.

## Presenter Mode

Development: **http://localhost:3030/presenter/1**.
Production preview: **http://127.0.0.1:4173/#/presenter/1**.
Sub-path에서도 같은 `#/presenter/1` 형식을 사용합니다.

Audience view에서 **P** 또는 navigation bar의 presenter 버튼으로 진입할 수 있습니다.
Presenter view의 **Play Mode**는 audience view를 엽니다. 같은 origin의 두 창을
노트북/프로젝터에 배치하세요. Current/Next slide, notes, timer, navigation이 제공됩니다.
Timer는 시간 표시 옆 아이콘에 마우스를 올리면 나타나는 play/reset 제어로
시작/초기화할 수 있습니다. 두 창의 slide/click 이동은 같은 origin에서 동기화됩니다.

- **→ / Space**: 다음 click 단계 또는 slide
- **←**: 이전 단계 또는 slide
- Navigation bar: fullscreen, overview, presenter controls
- Slide 02: LLM → Jev → 핵심 문구, 3 clicks
- Slide 06: generation → decision → code + 핵심 문구, 3 clicks

## PDF Export

최초 한 번, Chromium을 준비합니다:

```bash
npm run browser:install
npm run export
```

Slidev 자체 exporter가 `exports/jev.pdf`를 만듭니다. 16:9, dark background,
**10페이지**이며 click 단계는 각 slide의 최종 상태로 합칩니다. Notes는 PDF에
포함하지 않습니다. `playwright-chromium`은 local devDependency입니다.
Offline 반입 전 이 설치를 완료하세요. Linux에서는 Playwright가 요구하는
Chromium OS libraries도 설치되어 있어야 합니다.

## PPTX Export

```bash
npm run export:pptx
```

`exports/jev.pptx`, **10장**, presenter notes 포함. Slidev의 image-based PPTX
export입니다. Slide는 이미지라 text/object editing과 click animation은 제공하지
않습니다. 웹 발표가 기본 실행 방식입니다. Export 결과물은 Git에서 제외됩니다.

## Live Demo

Dev **http://localhost:3030/9**, production **http://127.0.0.1:4173/#/9**가
terminal 전환 anchor입니다. 아래 CLI command는 **repository root**에서 실행합니다:

```bash
uv run jev-router-demo
```

Python/uv 설치와 `.env.local`은 [CLI README](../../README.md#configure)를 따릅니다.
LiteLLM/Ollama에 실제 모델을 준비하고 발표 전에 endpoint를 확인하세요.

1. Slide 09 → terminal → CLI 실행.
2. Python Utility: `r` + Enter. 두 Router에 같은 input이 전송됩니다.
3. `n` 두 번 → vLLM / CUDA Compatibility → `r` (Web).
4. `n` 두 번 → Production DB Cleanup → `r` (Approval).
5. Routing result, latency, input/output tokens, parse 확인. `v` 입력 전문,
   `o` generated/raw output, Enter 복귀.
6. `q` → browser 복귀 → **→ 한 번** → Slide 10 (`/10` 또는 `#/10`).

현재 **두 adapter 모두 generated JSON을 parse**합니다. Jev-like path는
Ollama `/api/generate` fallback이며 native typed Jev API가 아닙니다. Confidence는
미제공, `—`는 미관측입니다. Downstream agent/web/DB 작업은 실행하지 않습니다.
연결 실패는 실제 오류로 설명하며 임의의 성공 수치로 대체하지 않습니다.

## Content and timing

`talk.md`가 발표 내용·논리의 source of truth이고 `slides.md`는 Slidev용 visual
adaptation입니다. 내용 변경은 원고와 두 deck의 동일 메시지를 함께 확인하세요.
Reveal markup/runtime을 import하지 않습니다. Slide 04는 개념적 contract이며
공식 SDK API나 실측 probability를 주장하지 않습니다.

Notes: 0:40 / 1:10 / 1:30 / 1:30 / 1:40 / 1:30 / 1:30 / 1:00 / 3:00 / 1:30.
합계 15:00. Terminal 전환은 Live demo의 3:00에 포함합니다. 상세 원고 대신 짧은 설명,
transition, demo cues만 presenter notes에 기록했습니다.

## Project Structure

```text
presentation/
├── talk.md                    # 공유 원고, Reveal에서 직접 rendering
├── reveal/                    # 독립 Reveal.js 구현
└── slidev/
    ├── slides.md              # 10장 + presenter notes
    ├── style.css              # dark/cyan visual system, system fonts
    ├── components/
    │   ├── DecisionCard.vue
    │   └── MetricCard.vue
    ├── package.json
    ├── package-lock.json
    ├── dist/                  # generated, ignored
    └── exports/               # generated PDF/PPTX, ignored
```

Favicon도 `slides.md`에 inline SVG로 보관해 Slidev 기본 CDN 요청을 제거했습니다.
