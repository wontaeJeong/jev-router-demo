# Jev Slidev Presentation

**본문 15장 / 약 15분 + 보충 3장**. Markdown·Vue·CSS로 관리하는 개발자 대상 발표입니다.
`slides.md`가 슬라이드와 발표 노트의 단일 원본입니다. CLI live demo는 별도 터미널에서 진행합니다.

## Requirements / install

- Node.js **24 LTS**, npm 권장. Slidev의 최소 요구 버전은 22.12입니다.
- 한국어를 지원하는 OS system font. 원격 폰트·iframe·API 호출은 사용하지 않습니다.
- 최초 npm 설치와 export용 Chromium 다운로드는 인터넷이 필요합니다.

Repository root에서:

```bash
cd presentation/slidev
npm ci
npm run dev
```

Audience: **http://localhost:3030/1**. `--port 3030`으로 포트를 명시할 수 있습니다.
Slidev Twoslash와의 호환성을 위해 `floating-vue@5.2.2` override를 유지합니다.

## Build / preview

```bash
npm run build
npm run preview
```

결과물은 `dist/`, 기본 preview는 **http://127.0.0.1:4173/#/1**입니다.
`file://` 대신 HTTP 서버를 사용합니다. Hash routing으로 static hosting에서도
각 slide의 URL을 새로고침할 수 있습니다. 실행 시 표시된 실제 포트를 확인하세요.

GitHub Pages의 repository 경로를 로컬에서 재현하려면:

```bash
npm run build -- --base /jev-router-demo/
npm run preview -- --base /jev-router-demo/
```

Preview: **http://127.0.0.1:4173/jev-router-demo/#/1**.
Base는 `/`로 시작하고 끝납니다. 다른 repository·custom domain에 배포하면 해당 base로 변경하세요.
배포 workflow와 GitHub 설정은 [상위 README](../README.md#github-pages)를 참고하세요.

## Presenter / navigation

- Dev: **http://localhost:3030/presenter/1**.
- Preview: **http://127.0.0.1:4173/#/presenter/1**.
- Audience에서 **P** 또는 navigation bar의 presenter 버튼으로 진입.
- Presenter의 **Play Mode**로 audience 창을 열고 같은 origin의 두 창을 노트북/프로젝터에 배치.
- Current/Next slide, notes, timer 제공. Timer의 play/reset 제어로 시간 측정.
- **→ / Space**: 다음 단계 또는 slide. **←**: 이전 단계 또는 slide.
- Navigation bar: fullscreen, overview, presenter controls.

단계별 표시는 **4번(생성 → 판단 → 계약)**과 **8번(판단 → 생성/도구 → 실행 코드)**에
각 3 clicks입니다. PDF/PPTX에는 최종 상태를 한 장으로 합칩니다.

### Useful anchors

| 목적 | Dev | Static / Pages |
| --- | --- | --- |
| Live demo | `/13` | `#/13` |
| 결과 해석 | `/14` | `#/14` |
| Takeaway / Q&A | `/15` | `#/15` |
| 보충 자료 | `/16`–`/18` | `#/16`–`#/18` |

## PDF / PPTX

최초 한 번 Chromium을 준비한 후:

```bash
npm run browser:install
npm run export
npm run export:pptx
```

- PDF: `exports/jev.pdf`, **18페이지**, 16:9, dark background, notes 제외.
- PPTX: `exports/jev.pptx`, **18장**, presenter notes 포함. 각 slide는 이미지라
  PowerPoint에서 텍스트·도형을 개별 편집하거나 click animation을 재생할 수 없습니다.
- 본문만 PDF로 공유하려면 `npm run export -- --range 1-15`.
- 생성 결과물은 Git에서 제외합니다. `slides.md`를 수정한 뒤 다시 export하세요.
- Linux에서는 Playwright가 요구하는 Chromium OS libraries도 필요합니다.

설치·빌드 이후 로컬 HTTP로 audience/presenter를 실행하면 인터넷 없이 발표할 수 있습니다.
CLI 데모에는 별도의 로컬 모델 endpoint 준비가 필요합니다.

## Live demo

Python/uv와 `.env.local`은 [CLI README](../../README.md#configure)를 따릅니다.
LiteLLM/Ollama 모델을 준비한 뒤 **repository root**에서 실행:

```bash
uv run jev-router-demo --cli
```

1. Slide 13 → terminal → CLI 실행.
2. Python Utility: `r` + Enter. 두 Router의 Tier/Web/Approval부터 읽습니다.
3. `n` 두 번 → vLLM / CUDA Compatibility → `r` (Web).
4. `n` 두 번 → Production DB Cleanup → `r` (Approval).
5. Latency, 실제 input/output tokens, parse 비교. `v` 입력 전문, `o` generated/raw output.
6. `q` → 브라우저 복귀 → **→ 한 번** → Slide 14에서 결과 해석 → Slide 15 Q&A.

각 명령 뒤 Enter를 누릅니다. Reference route는 metadata이지 모델 판단을 덮어쓰는 값이 아닙니다.
LiteLLM만 generated JSON을 parse합니다. 로컬 Ollama를 포함한 Jev 경로는
`/v1/systemone` typed API를 사용하며 실제 반환된 candidate probabilities를 표시합니다.
`—`는 미관측입니다. 실제 웹 검색·DB 작업은 실행하지 않습니다.
연결 실패 시 실제 오류를 설명하고 임의의 성공 수치로 대체하지 않습니다.

## Content / timing

본문 notes 시간:
`0:30 / 0:50 / 1:00 / 0:50 / 0:50 / 1:00 / 0:50 / 1:00 / 0:50 / 0:50 / 0:50 / 0:40 / 3:00 / 1:00 / 1:00`.
합계 **15:00**. Terminal 전환은 demo의 3:00에 포함하며 보충 자료는 본문 시간에서 제외합니다.

한 slide에 한 주장, 결론형 한국어 제목, 같은 사례의 연속 사용이 편집 기준입니다.
Concept·설명용 값·현재 구현·실측을 구분합니다. `slides.md`의 HTML comments에
시간·전환 문장·데모 조작·세부 설명을 기록합니다.

## Structure

```text
presentation/
├── README.md
└── slidev/
    ├── slides.md              # 유일한 원고: 본문 15장 + 보충 3장 + notes
    ├── style.css              # dark/cyan visual system, system fonts
    ├── global-bottom.vue      # footer / page numbers
    ├── components/
    │   ├── DecisionCard.vue
    │   └── MetricCard.vue
    ├── package.json
    ├── package-lock.json
    ├── dist/                  # generated, ignored
    └── exports/               # generated, ignored
```

Favicon은 `slides.md`의 inline SVG로 제공해 CDN 요청을 피합니다.
